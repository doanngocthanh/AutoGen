import React, { useState } from 'react';
import axios from 'axios';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const { email, password } = formData;

  const onChange = (e) =>
    setFormData({ ...formData, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();
    try {
      const config = {
        headers: {
          'Content-Type': 'application/json',
        },
      };

      const body = JSON.stringify({ email, password });

      const res = await axios.post('/api/auth/login', body, config);
      console.log(res.data);
      // Store token and redirect
    } catch (err) {
      console.error(err.response.data);
    }
  };

  return (
    <form onSubmit={(e) => onSubmit(e)}>
      <div>
        <label>Email</label>
        <input
          type='email'
          name='email'
          value={email}
          onChange={(e) => onChange(e)}
          required
        />
      </div>
      <div>
        <label>Password</label>
        <input
          type='password'
          name='password'
          value={password}
          onChange={(e) => onChange(e)}
          required
        />
      </div>
      <button type='submit'>Login</button>
    </form>
  );
};

export default Login;