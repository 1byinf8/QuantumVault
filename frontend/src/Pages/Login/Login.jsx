// /Users/1byinf8/Documents/QRYPTOVAULT/frontend/src/Login.js
import React, { useState } from 'react';
import './Login.css';

export default function Login() {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    username: ''
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [serverMessage, setServerMessage] = useState({ type: '', text: '' });

  const API_URL = 'http://localhost:8000';

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });

    if (errors[name]) {
      setErrors({ ...errors, [name]: '' });
    }
  };

  const validate = () => {
    const newErrors = {};

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    if (!isLogin) {
      if (!formData.username) newErrors.username = 'Username is required';
      if (!formData.confirmPassword) {
        newErrors.confirmPassword = 'Please confirm your password';
      } else if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = 'Passwords do not match';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (validate()) {
      setIsLoading(true);
      setServerMessage({ type: '', text: '' });

      try {
        const dataToSend = { email: formData.email, password: formData.password };
        if (!isLogin) dataToSend.username = formData.username;

        const response = await fetch(`${API_URL}/${isLogin ? 'login' : 'signup'}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(dataToSend)
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || 'Request failed');
        }

        // Handle success
        setServerMessage({
          type: 'success',
          text: data.status || (isLogin ? 'Login successful!' : 'Signup successful! Please login.')
        });

        if (isLogin) {
          if (data.username) {  // Changed from token to username
            localStorage.setItem('loggedInUser', data.username);
            window.location.href = '/';  // Redirect to dashboard
          } else {
            throw new Error('Login successful but username missing.');
          }
        } else {
          setTimeout(() => {
            setIsLogin(true);
            setFormData({ email: '', password: '', confirmPassword: '', username: '' });
          }, 1000);
        }
      } catch (error) {
        console.error('Fetch error:', error.message, error.stack);
        setServerMessage({
          type: 'error',
          text: error.message || 'Something went wrong. Please try again.'
        });
      } finally {
        setIsLoading(false);
      }
    }
  };

  const toggleAuthMode = () => {
    setIsLogin(!isLogin);
    setErrors({});
    setServerMessage({ type: '', text: '' });
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2 className="auth-title">
          {isLogin ? `Welcome back, ${formData.username || 'User'}! Login to Your Account` : 'Create an Account'}
        </h2>

        {serverMessage.text && <div className={`server-message ${serverMessage.type}`}>{serverMessage.text}</div>}

        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <div className="form-group">
              <label className="form-label" htmlFor="username">Username</label>
              <input
                id="username"
                name="username"
                type="text"
                value={formData.username}
                onChange={handleChange}
                className={errors.username ? 'form-input error' : 'form-input'}
                placeholder="Enter your unique username"
              />
              {errors.username && <p className="error-message">{errors.username}</p>}
            </div>
          )}

          <div className="form-group">
            <label className="form-label" htmlFor="email">Email Address</label>
            <input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              className={errors.email ? 'form-input error' : 'form-input'}
              placeholder="Enter your email"
            />
            {errors.email && <p className="error-message">{errors.email}</p>}
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              className={errors.password ? 'form-input error' : 'form-input'}
              placeholder="Enter your password"
            />
            {errors.password && <p className="error-message">{errors.password}</p>}
          </div>

          {!isLogin && (
            <div className="form-group">
              <label className="form-label" htmlFor="confirmPassword">Confirm Password</label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                value={formData.confirmPassword}
                onChange={handleChange}
                className={errors.confirmPassword ? 'form-input error' : 'form-input'}
                placeholder="Confirm your password"
              />
              {errors.confirmPassword && <p className="error-message">{errors.confirmPassword}</p>}
            </div>
          )}

          <div className="form-group">
            <button type="submit" className="submit-button" disabled={isLoading}>
              {isLoading ? <span className="loading-spinner"></span> : isLogin ? 'Login' : 'Sign Up'}
            </button>
          </div>

          <div className="auth-switch">
            <p>
              {isLogin ? "Don't have an account? " : "Already have an account? "}
              <button type="button" onClick={toggleAuthMode} className="switch-button">
                {isLogin ? 'Sign up' : 'Login'}
              </button>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}