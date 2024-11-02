import React, { useState } from 'react';
import axios from 'axios';

function Register() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    axios.post('/api/register', { username, password })
      .then(response => {
        alert('Registration successful!');
        // Redirect to login page or automatically log in the user
        window.location.href = '/login';
      })
      .catch(error => {
        console.error('Registration error:', error);
        const errorMessage = error.response?.data?.message || 'Registration failed';
        alert(errorMessage);
      });
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Username"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      <button type="submit">Register</button>
    </form>
  );
}

export default Register;