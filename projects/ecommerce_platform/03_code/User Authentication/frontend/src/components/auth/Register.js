import React, { useState } from 'react';
import axios from 'axios';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password2: '',
  });

  const { username, email, password, password2 } = formData;

  const onChange = (e) =>
    setFormData({ ...formData, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();
    if (password !== password2) {
      console.log('Passwords do not match');
    } else {
      try {
        const config = {
          headers: {
            'Content-Type': 'application/json',
          },
        };

        const body = JSON.stringify({ username, email, password });

        const res = await axios.post('/api/auth/register', body, config);
        console.log(res.data);
        // Store token and redirect
      } catch (err) {
        console.error(err.response.data);
      }
    }
  };

  return (
    <form onSubmit={(e) => onSubmit(e)}>
      <div>
        <label>Username</label>
        <input
          type='text'
          name='username'
          value={username}
          onChange={(e) => onChange(e)}
          required
        />
      </div>
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
      <div>
        <label>Confirm Password</label>
        <input
          type='password'
          name='password2'
          value={password2}
          onChange={(e) => onChange(e)}
          required
        />
      </div>
      <button type='submit'>Register</button>
    </form>
  );
};

export default Register;