import asyncio
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from dataclasses import dataclass, asdict
import logging
from dotenv import load_dotenv

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProjectContext:
    """Shared context giữa các API"""
    project_name: str
    requirements: Optional[Dict] = None
    architecture: Optional[Dict] = None
    codebase: Optional[Dict] = None
    test_results: Optional[Dict] = None
    deployment: Optional[Dict] = None
    created_at: str = None
    current_stage: str = "not_started"
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

class RAGManager:
    """Quản lý RAG system để Gemini có thể rà soát lại source code"""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.source_index = {}
        self.file_contents = {}
        
    def scan_project_files(self) -> Dict[str, Any]:
        """Scan toàn bộ project để tạo index"""
        logger.info("🔍 Scanning project files for RAG system...")
        
        file_types = {
            ".py": "python",
            ".js": "javascript", 
            ".java": "java",
            ".sql": "sql",
            ".json": "json",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".md": "markdown",
            ".txt": "text",
            ".properties": "properties"
        }
        
        project_structure = {
            "files": {},
            "directories": [],
            "modules": {},
            "summary": {
                "total_files": 0,
                "file_types": {},
                "last_scan": datetime.now().isoformat()
            }
        }
        
        if not self.project_dir.exists():
            return project_structure
            
        for file_path in self.project_dir.rglob("*"):
            if file_path.is_file():
                try:
                    relative_path = file_path.relative_to(self.project_dir)
                    file_ext = file_path.suffix.lower()
                    file_type = file_types.get(file_ext, "unknown")
                    
                    # Đọc content file (limit size để tránh quá tải)
                    file_size = file_path.stat().st_size
                    if file_size < 50000:  # < 50KB
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                        except:
                            with open(file_path, 'r', encoding='latin-1') as f:
                                content = f.read()
                    else:
                        content = f"[File too large: {file_size} bytes]"
                    
                    project_structure["files"][str(relative_path)] = {
                        "type": file_type,
                        "size": file_size,
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                        "content_preview": content[:500] if len(content) > 500 else content
                    }
                    
                    # Full content cho files nhỏ
                    if file_size < 10000:  # < 10KB
                        self.file_contents[str(relative_path)] = content
                    
                    # Update statistics
                    project_structure["summary"]["total_files"] += 1
                    project_structure["summary"]["file_types"][file_type] = \
                        project_structure["summary"]["file_types"].get(file_type, 0) + 1
                        
                except Exception as e:
                    logger.warning(f"⚠️ Could not process file {file_path}: {e}")
            
            elif file_path.is_dir():
                relative_path = file_path.relative_to(self.project_dir)
                if relative_path != Path("."):
                    project_structure["directories"].append(str(relative_path))
        
        # Organize by modules
        for file_path in project_structure["files"]:
            parts = Path(file_path).parts
            if len(parts) > 1:
                module_name = parts[1] if parts[0] == "03_code" else parts[0]
                if module_name not in project_structure["modules"]:
                    project_structure["modules"][module_name] = []
                project_structure["modules"][module_name].append(file_path)
        
        self.source_index = project_structure
        logger.info(f"✅ Scanned {project_structure['summary']['total_files']} files")
        return project_structure
    
    def get_context_for_stage(self, stage: str) -> str:
        """Lấy context phù hợp cho từng stage"""
        if not self.source_index:
            self.scan_project_files()
        
        context_builders = {
            "requirements": self._build_requirements_context,
            "architecture": self._build_architecture_context,
            "code": self._build_code_context,
            "review": self._build_review_context,
            "deployment": self._build_deployment_context
        }
        
        builder = context_builders.get(stage, self._build_general_context)
        return builder()
    
    def _build_requirements_context(self) -> str:
        """Context cho requirements stage"""
        req_files = [f for f in self.source_index.get("files", {}) 
                    if "01_requirements" in f or "requirements" in f.lower()]
        
        context = "EXISTING REQUIREMENTS FILES:\n"
        for file_path in req_files:
            if file_path in self.file_contents:
                context += f"\n{file_path}:\n{self.file_contents[file_path]}\n"
        
        return context
    
    def _build_architecture_context(self) -> str:
        """Context cho architecture stage"""
        arch_files = [f for f in self.source_index.get("files", {}) 
                     if "02_architecture" in f or "architecture" in f.lower()]
        req_files = [f for f in self.source_index.get("files", {}) 
                    if "01_requirements" in f]
        
        context = "EXISTING ARCHITECTURE & REQUIREMENTS:\n"
        
        # Add requirements context
        for file_path in req_files:
            if file_path in self.file_contents:
                context += f"\nREQUIREMENTS - {file_path}:\n{self.file_contents[file_path]}\n"
        
        # Add architecture context  
        for file_path in arch_files:
            if file_path in self.file_contents:
                context += f"\nARCHITECTURE - {file_path}:\n{self.file_contents[file_path]}\n"
        
        return context
    
    def _build_code_context(self) -> str:
        """Context cho code generation stage"""
        relevant_files = []
        
        # Requirements và Architecture
        for pattern in ["01_requirements", "02_architecture"]:
            relevant_files.extend([f for f in self.source_index.get("files", {}) if pattern in f])
        
        # Existing code files
        code_files = [f for f in self.source_index.get("files", {}) if "03_code" in f]
        
        context = "PROJECT CONTEXT FOR CODE GENERATION:\n\n"
        
        # Add previous stages
        for file_path in relevant_files:
            if file_path in self.file_contents:
                stage = "REQUIREMENTS" if "01_" in file_path else "ARCHITECTURE"
                context += f"{stage} - {file_path}:\n{self.file_contents[file_path]}\n\n"
        
        # Add existing code structure
        if code_files:
            context += "EXISTING CODE STRUCTURE:\n"
            modules = self.source_index.get("modules", {})
            for module_name, files in modules.items():
                if any("03_code" in f for f in files):
                    context += f"\nModule: {module_name}\n"
                    for file_path in files[:5]:  # Limit số files
                        if "03_code" in file_path and file_path in self.file_contents:
                            context += f"  {file_path}: {len(self.file_contents[file_path])} chars\n"
        
        return context
    
    def _build_review_context(self) -> str:
        """Context cho review stage"""
        code_files = [f for f in self.source_index.get("files", {}) if "03_code" in f]
        
        context = "CODE FILES FOR REVIEW:\n\n"
        
        # Group by modules
        modules = self.source_index.get("modules", {})
        for module_name, files in modules.items():
            module_code_files = [f for f in files if "03_code" in f]
            if module_code_files:
                context += f"MODULE: {module_name}\n"
                for file_path in module_code_files[:10]:  # Limit files
                    file_info = self.source_index["files"].get(file_path, {})
                    context += f"  - {file_path} ({file_info.get('type', 'unknown')}, {file_info.get('size', 0)} bytes)\n"
                    
                    # Add preview cho files quan trọng
                    if file_path in self.file_contents and any(ext in file_path for ext in ['.py', '.js', '.java']):
                        preview = self.file_contents[file_path][:300]
                        context += f"    Preview: {preview}...\n"
                context += "\n"
        
        return context
    
    def _build_deployment_context(self) -> str:
        """Context cho deployment stage"""
        all_stages = ["01_requirements", "02_architecture", "03_code", "04_tests"]
        
        context = "COMPLETE PROJECT CONTEXT FOR DEPLOYMENT:\n\n"
        
        # Project summary
        summary = self.source_index.get("summary", {})
        context += f"Project Summary:\n"
        context += f"- Total files: {summary.get('total_files', 0)}\n"
        context += f"- File types: {summary.get('file_types', {})}\n"
        context += f"- Modules: {list(self.source_index.get('modules', {}).keys())}\n\n"
        
        # Key files from each stage
        for stage in all_stages:
            stage_files = [f for f in self.source_index.get("files", {}) if stage in f]
            if stage_files:
                stage_name = stage.split("_")[1].upper()
                context += f"{stage_name} FILES:\n"
                for file_path in stage_files[:3]:  # Top 3 files per stage
                    if file_path in self.file_contents:
                        context += f"  {file_path}:\n{self.file_contents[file_path][:200]}...\n\n"
        
        return context
    
    def _build_general_context(self) -> str:
        """General context"""
        return f"PROJECT STRUCTURE:\n{json.dumps(self.source_index, indent=2, ensure_ascii=False)}"
    
    def save_rag_index(self):
        """Lưu RAG index ra file"""
        index_file = self.project_dir / "rag_index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(self.source_index, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Saved RAG index to {index_file}")

class GeminiAPIManager:
    """Quản lý 5 API Gemini với vai trò chuyên biệt"""
    
    def __init__(self, api_keys: List[str]):
        self.api_keys = api_keys
        self.models = {}
        self.setup_models()
        
        # Định nghĩa system prompts cho từng API
        self.system_prompts = {
            "planner": """You are a senior business analyst and product manager. 
            Analyze requirements and create detailed specifications.
            
            RETURN ONLY VALID JSON with this structure:
            {
                "requirements": ["req1", "req2", "req3"],
                "user_stories": ["story1", "story2"],
                "acceptance_criteria": ["criteria1", "criteria2"],
                "timeline": "estimated timeline",
                "priority": "high/medium/low"
            }
            
            Keep strings short and avoid multiline content.""",
            
            "architect": """You are a system architect with 15+ years experience.
            Design scalable architectures and database schemas.
            
            RETURN ONLY VALID JSON with this structure:
            {
                "architecture_type": "microservices/monolith",
                "tech_stack": {
                    "backend": "framework name",
                    "frontend": "framework name",
                    "database": "database type"
                },
                "database_schema": "brief description",
                "api_design": "RESTful API design summary",
                "modules": ["module1", "module2", "module3"]
            }
            
            Keep all values as simple strings or arrays.""",
            
            "developer": """You are a senior full-stack developer.
            Generate file structure and code organization plan.
            
            RETURN ONLY VALID JSON with this structure:
            {
                "modules": ["backend", "frontend", "database"],
                "file_structure": {
                    "backend/": "API server files",
                    "frontend/": "UI application files",
                    "database/": "Schema and migration files"
                },
                "dependencies": ["package1", "package2"],
                "code_files": {
                    "README.md": "Project setup instructions",
                    "requirements.txt": "python package list"
                }
            }
            
            For code_files, only include SHORT file contents or descriptions.""",
            
            "reviewer": """You are a code review expert and QA engineer.
            Review code quality and generate test plans.
            
            RETURN ONLY VALID JSON with this structure:
            {
                "code_quality_score": 85,
                "issues": ["issue1", "issue2"],
                "suggestions": ["suggestion1", "suggestion2"],
                "test_files": {
                    "test_api.py": "API test descriptions",
                    "test_ui.py": "UI test descriptions"
                },
                "security_report": "security assessment summary"
            }
            
            Keep all descriptions short and concise.""",
            
            "devops": """You are a DevOps engineer specializing in CI/CD and cloud deployment.
            Create deployment configurations summary.
            
            RETURN ONLY VALID JSON with this structure:
            {
                "docker_files": {
                    "Dockerfile": "Docker configuration summary",
                    "docker-compose.yml": "Multi-service setup"
                },
                "ci_cd_config": {
                    ".github/workflows/deploy.yml": "CI/CD pipeline summary"
                },
                "k8s_manifests": {
                    "deployment.yaml": "K8s deployment config"
                },
                "deployment_guide": "step-by-step deployment summary"
            }
            
            Provide summaries and descriptions, not full file contents."""
        }
    
    def setup_models(self):
        """Khởi tạo 5 model Gemini với API keys khác nhau"""
        for i, api_key in enumerate(self.api_keys):
            genai.configure(api_key=api_key)
            model_name = ['planner', 'architect', 'developer', 'reviewer', 'devops'][i]
            self.models[model_name] = genai.GenerativeModel('gemini-2.0-flash')
            logger.info(f"Initialized {model_name} model with API key {i+1}")
    
    async def call_api(self, model_name: str, prompt: str, context: ProjectContext, rag_context: str = "") -> Dict:
        """Gọi API với error handling và retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Tạo full prompt với system prompt + context + RAG + user prompt
                full_prompt = f"""
{self.system_prompts[model_name]}

PROJECT CONTEXT:
{json.dumps(asdict(context), indent=2, ensure_ascii=False)}

RAG CONTEXT (EXISTING PROJECT FILES):
{rag_context}

USER REQUEST:
{prompt}

CRITICAL JSON FORMATTING RULES:
1. Use file paths as keys, not actual code content in JSON
2. For code files: use "file_path": "description" format
3. Never include multiline code directly in JSON values
4. Use escaped strings for short code snippets only
5. Response must be valid JSON - test it before sending

IMPORTANT: Review the RAG context to understand existing project structure and continue from where previous work left off.
"""
                
                model = self.models[model_name]
                
                # Cấu hình generation để tránh response quá dài
                generation_config = {
                    "temperature": 0.1,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 8192,
                }
                
                response = model.generate_content(full_prompt, generation_config=generation_config)
                
                # Parse JSON response với nhiều cách thử
                response_text = response.text.strip()
                result = self.parse_json_response(response_text, model_name, attempt)
                
                if result:
                    logger.info(f"✅ {model_name} API call successful")
                    return result
                    
            except Exception as e:
                logger.error(f"❌ API call error in {model_name}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    # Trả về structure mặc định thay vì raise exception
                    return self.get_default_structure(model_name)
    
    def parse_json_response(self, response_text: str, model_name: str, attempt: int) -> Optional[Dict]:
        """Parse JSON response với nhiều strategy"""
        parsing_strategies = [
            self.parse_clean_json,
            self.parse_markdown_json, 
            self.parse_partial_json,
            self.parse_line_by_line_json
        ]
        
        for i, strategy in enumerate(parsing_strategies):
            try:
                result = strategy(response_text)
                if result:
                    logger.info(f"✅ JSON parsed using strategy {i+1} for {model_name}")
                    return result
            except Exception as e:
                logger.debug(f"Strategy {i+1} failed for {model_name}: {e}")
                continue
        
        logger.error(f"❌ All JSON parsing strategies failed for {model_name} (attempt {attempt+1})")
        return None
    
    def parse_clean_json(self, text: str) -> Dict:
        """Parse JSON trực tiếp"""
        return json.loads(text.strip())
    
    def parse_markdown_json(self, text: str) -> Dict:
        """Parse JSON từ markdown blocks"""
        if '```json' in text:
            json_content = text.split('```json')[1].split('```')[0].strip()
            return json.loads(json_content)
        elif '```' in text:
            json_content = text.split('```')[1].split('```')[0].strip()
            return json.loads(json_content)
        raise ValueError("No markdown JSON found")
    
    def parse_partial_json(self, text: str) -> Dict:
        """Tìm và parse JSON object đầu tiên"""
        start = text.find('{')
        if start == -1:
            raise ValueError("No JSON object found")
        
        brace_count = 0
        end = start
        
        for i in range(start, len(text)):
            if text[i] == '{':
                brace_count += 1
            elif text[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end = i + 1
                    break
        
        if brace_count != 0:
            raise ValueError("Incomplete JSON object")
        
        json_str = text[start:end]
        return json.loads(json_str)
    
    def parse_line_by_line_json(self, text: str) -> Dict:
        """Parse JSON từng dòng để tìm lỗi"""
        lines = text.split('\n')
        json_lines = []
        in_json = False
        
        for line in lines:
            if line.strip().startswith('{') or in_json:
                in_json = True
                json_lines.append(line)
                if line.strip().endswith('}') and line.count('}') >= line.count('{'):
                    break
        
        if not json_lines:
            raise ValueError("No JSON content found")
        
        json_str = '\n'.join(json_lines)
        
        # Fix common JSON issues
        json_str = self.fix_common_json_issues(json_str)
        
        return json.loads(json_str)
    
    def fix_common_json_issues(self, json_str: str) -> str:
        """Fix common JSON formatting issues"""
        # Remove trailing commas
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # Fix unescaped quotes in strings (basic fix)  
        json_str = re.sub(r'(?<!\\)"(?![,\]\}:\s])', r'\\"', json_str)
        
        # Remove control characters
        json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
        
        return json_str
    
    def get_default_structure(self, model_name: str) -> Dict:
        """Trả về structure mặc định khi parse JSON thất bại"""
        default_structures = {
            "planner": {
                "requirements": ["Parse failed - manual review needed"],
                "user_stories": ["Parse failed - manual review needed"],
                "acceptance_criteria": ["Parse failed - manual review needed"],
                "timeline": "Parse failed - manual review needed",
                "status": "partial_failure"
            },
            "architect": {
                "architecture_type": "microservices", 
                "tech_stack": {
                    "backend": "FastAPI",
                    "frontend": "React",
                    "database": "PostgreSQL"
                },
                "database_schema": "Parse failed - manual review needed",
                "api_design": "Parse failed - manual review needed",
                "status": "partial_failure"
            },
            "developer": {
                "modules": ["backend", "frontend", "database"],
                "file_structure": {
                    "backend/": "FastAPI application structure",
                    "frontend/": "React application structure", 
                    "database/": "Database migration files"
                },
                "code_files": {
                    "README.md": "# Project generated with parsing issues\nManual review required."
                },
                "dependencies": ["fastapi", "react", "postgresql"],
                "status": "partial_failure"
            },
            "reviewer": {
                "code_quality_score": 0,
                "issues": ["JSON parsing failed - manual code review required"],
                "suggestions": ["Fix JSON parsing issues", "Manual code review needed"],
                "test_files": {},
                "security_report": "Parse failed - manual review needed",
                "status": "partial_failure"
            },
            "devops": {
                "docker_files": {
                    "Dockerfile": "# Parse failed - manual creation needed"
                },
                "ci_cd_config": {
                    ".github/workflows/deploy.yml": "# Parse failed - manual creation needed"
                },
                "k8s_manifests": {},
                "deployment_guide": "Parse failed - manual review needed",
                "status": "partial_failure"
            }
        }
        
        return default_structures.get(model_name, {"error": "Unknown model", "status": "failure"})

class ProjectWorkflowManager:
    """Quản lý workflow chính của dự án"""
    
    def __init__(self, api_manager: GeminiAPIManager, project_name: str):
        self.api_manager = api_manager
        self.project_name = project_name
        self.context = ProjectContext(project_name=project_name)
        self.project_dir = Path(f"projects/{project_name}")
        self.rag_manager = RAGManager(self.project_dir)
        self.setup_project_structure()
        
        # Load existing context nếu có
        self.load_existing_context()
    
    def setup_project_structure(self):
        """Tạo cấu trúc thư mục dự án"""
        directories = [
            "01_requirements",
            "02_architecture", 
            "03_code",
            "04_tests",
            "05_deployment",
            "logs"
        ]
        
        for dir_name in directories:
            (self.project_dir / dir_name).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📁 Created project structure for {self.project_name}")
    
    def load_existing_context(self):
        """Load existing project context nếu có"""
        context_file = self.project_dir / "project_context.json"
        if context_file.exists():
            try:
                with open(context_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Restore context
                self.context.requirements = data.get('requirements')
                self.context.architecture = data.get('architecture')
                self.context.codebase = data.get('codebase')
                self.context.test_results = data.get('test_results')
                self.context.deployment = data.get('deployment')
                self.context.current_stage = data.get('current_stage', 'not_started')
                
                logger.info(f"📂 Loaded existing context from {context_file}")
                logger.info(f"🔄 Current stage: {self.context.current_stage}")
                
            except Exception as e:
                logger.warning(f"⚠️ Could not load existing context: {e}")
    
    def save_context(self):
        """Lưu context hiện tại"""
        context_file = self.project_dir / "project_context.json"
        with open(context_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(self.context), f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Saved context to {context_file}")
    
    def save_stage_output(self, stage: str, data: Dict, filename: str = None):
        """Lưu output của mỗi giai đoạn ra file"""
        if not filename:
            filename = f"{stage}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        stage_dirs = {
            "requirements": "01_requirements",
            "architecture": "02_architecture", 
            "code": "03_code",
            "review": "04_tests",
            "deployment": "05_deployment"
        }
        
        file_path = self.project_dir / stage_dirs[stage] / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Saved {stage} output to {file_path}")
        return file_path
    
    async def stage_1_requirements(self, user_input: str):
        """Giai đoạn 1: Phân tích requirements"""
        logger.info("🎯 Stage 1: Requirements Analysis")
        self.context.current_stage = "requirements"
        
        # Get RAG context
        rag_context = self.rag_manager.get_context_for_stage("requirements")
        
        prompt = f"""
        Analyze this project request and create detailed requirements:
        
        {user_input}
        
        Create comprehensive requirements document with user stories and acceptance criteria.
        Review any existing requirements in the RAG context and build upon them.
        """
        
        result = await self.api_manager.call_api("planner", prompt, self.context, rag_context)
        self.context.requirements = result
        
        # Lưu file và context
        self.save_stage_output("requirements", result)
        self.save_context()
        return result
    
    async def stage_2_architecture(self):
        """Giai đoạn 2: Thiết kế kiến trúc"""
        logger.info("🏗 Stage 2: Architecture Design")
        self.context.current_stage = "architecture"
        
        # Get RAG context
        rag_context = self.rag_manager.get_context_for_stage("architecture")
        
        prompt = """
        Based on the requirements, design a complete system architecture.
        Include technology stack, database design, API structure, and system diagrams.
        Consider scalability, security, and performance requirements.
        Review existing architecture files and build upon or refine them.
        """
        
        result = await self.api_manager.call_api("architect", prompt, self.context, rag_context)
        self.context.architecture = result
        
        self.save_stage_output("architecture", result)
        self.save_context()
        return result
    
    async def stage_3_code_generation(self):
        """Giai đoạn 3: Sinh code (có thể song song)"""
        logger.info("💻 Stage 3: Code Generation")
        self.context.current_stage = "code"
        
        # Scan existing files first
        self.rag_manager.scan_project_files()
        
        # Lấy danh sách modules từ architecture
        modules = self.context.architecture.get('modules', ['backend', 'frontend', 'database'])
        
        # Get RAG context
        rag_context = self.rag_manager.get_context_for_stage("code")
        
        # Chạy song song cho các modules với prompt cụ thể
        tasks = []
        for module in modules:
            prompt = f"""
            Create file structure and basic setup for the {module} module.
            
            Focus on:
            - Directory structure
            - Key configuration files  
            - Main entry points
            - Dependencies list
            
            DO NOT include full source code in JSON - only file descriptions and short configs.
            Review existing code structure in RAG context and continue from where it left off.
            """
            
            task = self.generate_module_code(module, prompt, rag_context)
            tasks.append(task)
        
        # Chờ tất cả modules hoàn thành
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"❌ Error in parallel code generation: {e}")
            results = [self.api_manager.get_default_structure("developer") for _ in modules]
        
        # Combine results
        combined_result = {
            "modules": {},
            "file_structure": {},
            "dependencies": [],
            "status": "completed"
        }
        
        for i, module in enumerate(modules):
            if isinstance(results[i], Exception):
                logger.error(f"❌ Module {module} generation failed: {results[i]}")
                combined_result["modules"][module] = self.api_manager.get_default_structure("developer")
                combined_result["status"] = "partial_failure"
            else:
                combined_result["modules"][module] = results[i]
                
                # Merge dependencies
                module_deps = results[i].get("dependencies", [])
                combined_result["dependencies"].extend(module_deps)
        
        # Remove duplicate dependencies
        combined_result["dependencies"] = list(set(combined_result["dependencies"]))
        
        self.context.codebase = combined_result
        self.save_stage_output("code", combined_result)
        
        # Tạo files code thực tế
        await self.create_code_files(combined_result)
        
        # Update RAG index after creating files
        self.rag_manager.scan_project_files()
        self.rag_manager.save_rag_index()
        
        self.save_context()
        return combined_result
    
    async def generate_module_code(self, module_name: str, prompt: str, rag_context: str):
        """Sinh code cho một module cụ thể"""
        logger.info(f"⚙️ Generating code for {module_name}")
        
        result = await self.api_manager.call_api("developer", prompt, self.context, rag_context)
        return result
    
    async def create_code_files(self, codebase_data: Dict):
        """Tạo các file code thực tế từ JSON data"""
        code_dir = self.project_dir / "03_code"
        
        for module_name, module_data in codebase_data.get("modules", {}).items():
            module_dir = code_dir / module_name
            module_dir.mkdir(exist_ok=True)
            
            # Tạo files từ code_files
            if "code_files" in module_data:
                for file_path, file_content in module_data["code_files"].items():
                    full_path = module_dir / file_path
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(file_content)
                    
                    logger.info(f"📄 Created {full_path}")
    
    async def stage_4_review_and_test(self):
        """Giai đoạn 4: Review code và tạo tests"""
        logger.info("🧪 Stage 4: Code Review & Testing")
        self.context.current_stage = "review"
        
        # Scan existing files first
        self.rag_manager.scan_project_files()
        
        # Get RAG context
        rag_context = self.rag_manager.get_context_for_stage("review")
        
        prompt = """
        Review the generated codebase for:
        1. Code quality and best practices
        2. Security vulnerabilities  
        3. Performance issues
        4. Generate comprehensive unit tests
        5. Integration tests
        6. Provide improvement suggestions
        
        Use the RAG context to understand the current codebase structure and create appropriate tests.
        """
        
        result = await self.api_manager.call_api("reviewer", prompt, self.context, rag_context)
        self.context.test_results = result
        
        self.save_stage_output("review", result)
        
        # Tạo test files nếu có
        if "test_files" in result:
            await self.create_test_files(result["test_files"])
        
        self.save_context()
        return result
    
    async def create_test_files(self, test_data: Dict):
        """Tạo test files"""
        test_dir = self.project_dir / "04_tests"
        
        for file_path, file_content in test_data.items():
            full_path = test_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            logger.info(f"🧪 Created test file {full_path}")
    
    async def stage_5_deployment(self):
        """Giai đoạn 5: Tạo deployment configs"""
        logger.info("🔄 Stage 5: Deployment & DevOps")
        self.context.current_stage = "deployment"
        
        # Scan existing files first
        self.rag_manager.scan_project_files()
        
        # Get RAG context
        rag_context = self.rag_manager.get_context_for_stage("deployment")
        
        prompt = """
        Create complete deployment configuration:
        1. Dockerfile for each service
        2. Docker Compose for local development
        3. Kubernetes manifests for production
        4. CI/CD pipeline (GitHub Actions)
        5. Deployment scripts and documentation
        6. Monitoring and logging setup
        
        Use the RAG context to understand the complete project structure and create appropriate deployment configs.
        """
        
        result = await self.api_manager.call_api("devops", prompt, self.context, rag_context)
        self.context.deployment = result
        
        self.save_stage_output("deployment", result)
        
        # Tạo deployment files với safe path handling
        await self.create_deployment_files_safe(result)
        
        self.save_context()
        return result
    
    async def create_deployment_files_safe(self, deployment_data: Dict):
        """Tạo deployment files với safe path handling"""
        deploy_dir = self.project_dir / "05_deployment"
        
        file_mappings = {
            "docker_files": "docker",
            "ci_cd_config": "ci-cd", 
            "k8s_manifests": "kubernetes"
        }
        
        for data_key, folder_name in file_mappings.items():
            if data_key in deployment_data:
                folder_path = deploy_dir / folder_name
                folder_path.mkdir(parents=True, exist_ok=True)  # Ensure parents exist
                
                files_data = deployment_data[data_key]
                if isinstance(files_data, dict):
                    for file_name, file_content in files_data.items():
                        # Safe file path handling
                        try:
                            # Clean file name và tạo safe path
                            safe_file_name = re.sub(r'[<>:"/\\|?*]', '_', file_name)
                            file_path = folder_path / safe_file_name
                            
                            # Ensure parent directory exists
                            file_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            # Write file content
                            content = file_content if isinstance(file_content, str) else str(file_content)
                            
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            
                            logger.info(f"🚀 Created deployment file {file_path}")
                            
                        except Exception as e:
                            logger.error(f"❌ Failed to create deployment file {file_name}: {e}")
                            # Create a simple text file with the error
                            error_file = folder_path / f"error_{safe_file_name}.txt"
                            with open(error_file, 'w', encoding='utf-8') as f:
                                f.write(f"Error creating {file_name}: {e}\n\nOriginal content:\n{file_content}")
                            logger.info(f"📝 Created error file {error_file}")
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Lấy status của workflow hiện tại"""
        stages = {
            "requirements": self.context.requirements is not None,
            "architecture": self.context.architecture is not None,
            "code": self.context.codebase is not None,
            "review": self.context.test_results is not None,
            "deployment": self.context.deployment is not None
        }
        
        completed_stages = sum(stages.values())
        total_stages = len(stages)
        
        return {
            "current_stage": self.context.current_stage,
            "stages": stages,
            "progress": f"{completed_stages}/{total_stages}",
            "percentage": (completed_stages / total_stages) * 100,
            "project_dir": str(self.project_dir),
            "last_updated": datetime.now().isoformat()
        }
    
    async def resume_workflow(self, user_input: str = None):
        """Resume workflow từ stage hiện tại"""
        status = self.get_workflow_status()
        logger.info(f"🔄 Resuming workflow from stage: {self.context.current_stage}")
        logger.info(f"📊 Progress: {status['progress']} ({status['percentage']:.1f}%)")
        
        # Determine next stage to run
        if not self.context.requirements:
            if not user_input:
                raise ValueError("User input required for requirements stage")
            await self.stage_1_requirements(user_input)
        
        if not self.context.architecture:
            await self.stage_2_architecture()
        
        if not self.context.codebase:
            await self.stage_3_code_generation()
        
        if not self.context.test_results:
            await self.stage_4_review_and_test()
        
        if not self.context.deployment:
            await self.stage_5_deployment()
        
        # Mark as completed
        self.context.current_stage = "completed"
        self.save_context()
        
        logger.info("✅ Workflow completed successfully!")
        return self.context
    
    async def run_full_workflow(self, user_input: str):
        """Chạy toàn bộ workflow"""
        logger.info(f"🚀 Starting full workflow for project: {self.project_name}")
        
        try:
            # Check if workflow is already in progress
            if self.context.current_stage != "not_started":
                logger.info(f"🔄 Resuming existing workflow from stage: {self.context.current_stage}")
                return await self.resume_workflow(user_input)
            
            # Stage 1: Requirements
            await self.stage_1_requirements(user_input)
            
            # Stage 2: Architecture  
            await self.stage_2_architecture()
            
            # Stage 3: Code Generation
            await self.stage_3_code_generation()
            
            # Stage 4: Review & Test
            await self.stage_4_review_and_test()
            
            # Stage 5: Deployment
            await self.stage_5_deployment()
            
            # Mark as completed
            self.context.current_stage = "completed"
            self.save_context()
            
            # Final RAG index save
            self.rag_manager.scan_project_files()
            self.rag_manager.save_rag_index()
            
            logger.info(f"✅ Workflow completed successfully!")
            logger.info(f"📁 Project files saved in: {self.project_dir}")
            
            return self.context
            
        except Exception as e:
            logger.error(f"❌ Workflow failed: {e}")
            # Save current progress
            self.save_context()
            raise

class WorkflowCLI:
    """Command Line Interface cho workflow management"""
    
    def __init__(self, project_name: str):
        load_dotenv()
        
        self.API_KEYS = [
            os.getenv("GEMINI_API_KEY_1"),
            os.getenv("GEMINI_API_KEY_2"),
            os.getenv("GEMINI_API_KEY_3"),
            os.getenv("GEMINI_API_KEY_4"),
            os.getenv("GEMINI_API_KEY_5"),
        ]
        
        self.api_manager = GeminiAPIManager(self.API_KEYS)
        self.workflow = ProjectWorkflowManager(self.api_manager, project_name)
    
    async def status(self):
        """Show workflow status"""
        status = self.workflow.get_workflow_status()
        
        print(f"\n🔍 PROJECT STATUS: {self.workflow.project_name}")
        print(f"📍 Current Stage: {status['current_stage']}")
        print(f"📊 Progress: {status['progress']} ({status['percentage']:.1f}%)")
        print(f"📁 Project Directory: {status['project_dir']}")
        print(f"🕐 Last Updated: {status['last_updated']}")
        
        print(f"\n📋 STAGE COMPLETION:")
        for stage, completed in status['stages'].items():
            icon = "✅" if completed else "⏳"
            print(f"  {icon} {stage.capitalize()}")
        
        return status
    
    async def resume(self, user_input: str = None):
        """Resume workflow from current stage"""
        return await self.workflow.resume_workflow(user_input)
    
    async def run(self, user_input: str):
        """Run full workflow"""
        return await self.workflow.run_full_workflow(user_input)
    
    async def scan_files(self):
        """Scan and show project files"""
        index = self.workflow.rag_manager.scan_project_files()
        
        print(f"\n📂 PROJECT FILES SCAN:")
        print(f"📊 Total Files: {index['summary']['total_files']}")
        print(f"📁 Directories: {len(index['directories'])}")
        print(f"🔧 Modules: {len(index['modules'])}")
        
        print(f"\n📈 FILE TYPES:")
        for file_type, count in index['summary']['file_types'].items():
            print(f"  {file_type}: {count}")
        
        print(f"\n📦 MODULES:")
        for module, files in index['modules'].items():
            print(f"  {module}: {len(files)} files")
        
        return index

# Usage Example
async def main():
    """Ví dụ sử dụng hệ thống với RAG và resume capability"""
    
    project_name = "ecommerce_platform"
    cli = WorkflowCLI(project_name)
    
    # Check current status
    await cli.status()
    
    # Input từ user
    user_request = """
    Tôi muốn xây dựng một nền tảng thương mại điện tử với các tính năng:
    - Quản lý sản phẩm và danh mục
    - Giỏ hàng và thanh toán
    - Quản lý đơn hàng
    - Hệ thống user và authentication
    - Admin dashboard
    - API cho mobile app
    - Tích hợp thanh toán VNPay, Momo
    - Hỗ trợ multi-language (Vietnamese, English)
    """
    
    try:
        # Chạy hoặc resume workflow
        if cli.workflow.context.current_stage == "not_started":
            print("🚀 Starting new workflow...")
            result = await cli.run(user_request)
        else:
            print("🔄 Resuming existing workflow...")
            result = await cli.resume(user_request)
        
        # Show final status
        await cli.status()
        
        # Scan final files
        await cli.scan_files()
        
        print("🎉 Project generation completed!")
        print(f"📁 Files saved in: {cli.workflow.project_dir}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💾 Progress has been saved. You can resume later.")
        await cli.status()

if __name__ == "__main__":
    asyncio.run(main())