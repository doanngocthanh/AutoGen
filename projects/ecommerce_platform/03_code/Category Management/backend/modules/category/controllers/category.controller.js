const Category = require('../models/category.model');

// Create a new category
exports.create = async (req, res) => {
  try {
    const category = await Category.create(req.body);
    res.status(201).json(category);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// Get all categories
exports.findAll = async (req, res) => {
  try {
    const categories = await Category.findAll();
    res.status(200).json(categories);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// Get a category by ID
exports.findOne = async (req, res) => {
  try {
    const category = await Category.findByPk(req.params.id);
    if (category) {
      res.status(200).json(category);
    } else {
      res.status(404).json({ message: 'Category not found' });
    }
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// Update a category by ID
exports.update = async (req, res) => {
  try {
    const category = await Category.update(req.body, {
      where: { id: req.params.id },
    });
    if (category[0] > 0) {
      res.status(200).json({ message: 'Category updated successfully' });
    } else {
      res.status(404).json({ message: 'Category not found' });
    }
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// Delete a category by ID
exports.delete = async (req, res) => {
  try {
    const category = await Category.destroy({
      where: { id: req.params.id },
    });
    if (category) {
      res.status(200).json({ message: 'Category deleted successfully' });
    } else {
      res.status(404).json({ message: 'Category not found' });
    }
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};