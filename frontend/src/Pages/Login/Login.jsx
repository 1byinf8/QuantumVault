import React, { useState } from 'react';
import './Login.css';

export default function Login(){
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: ''
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [serverMessage, setServerMessage] = useState({ type: '', text: '' });

  // API URL - replace with your actual backend endpoint
  const API_URL = 'https://localhost:8000';

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
    
    // Clear error when user types
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: ''
      });
    }
  };

  const validate = () => {
    const newErrors = {};
    
    // Email validation
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    
    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    // Signup specific validations
    if (!isLogin) {
      if (!formData.name) {
        newErrors.name = 'Name is required';
      }
      
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
        // Prepare data for API request
        const dataToSend = {
          email: formData.email,
          password: formData.password
        };
        
        // Add name for signup requests
        if (!isLogin) {
          dataToSend.name = formData.name;
        }
        
        // Make API request
        const response = await fetch(`${API_URL}/${isLogin ? 'login' : 'signup'}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(dataToSend)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          // Handle server validation errors
          if (data.errors) {
            setErrors(data.errors);
          } else {
            throw new Error(data.message || 'Authentication failed');
          }
        } else {
          // Successful authentication
          setServerMessage({
            type: 'success',
            text: data.message || `${isLogin ? 'Login' : 'Signup'} successful!`
          });
          
          // Handle successful login/signup
          if (data.token) {
            // Store token in localStorage or sessionStorage
            localStorage.setItem('authToken', data.token);
            
            // You can also store user info if returned from the server
            if (data.user) {
              localStorage.setItem('user', JSON.stringify(data.user));
            }
            
            // Redirect user or update app state
            // window.location.href = '/dashboard'; // Uncomment to redirect
          }
          
          // Reset form after successful signup
          if (!isLogin) {
            setFormData({
              email: '',
              password: '',
              confirmPassword: '',
              name: ''
            });
          }
        }
      } catch (error) {
        setServerMessage({
          type: 'error',
          text: error.message || 'Something went wrong. Please try again.'
        });
      } finally {
        setIsLoading(false);
      }
    }
  };

  // Function to check if username/email is unique
  const checkEmailUniqueness = async (email) => {
    if (!email || !/\S+@\S+\.\S+/.test(email)) return;
    
    try {
      const response = await fetch(`${API_URL}/check-email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email })
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        setErrors(prev => ({
          ...prev,
          email: data.message || 'This email is already taken'
        }));
      }
    } catch (error) {
      console.error('Error checking email uniqueness:', error);
    }
  };
  const checkUserNameUniqueness = async (name) => {
    try {
      const response = await fetch(`${API_URL}/check-userName`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name })
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        setErrors(prev => ({
          ...prev,
          name: data.message || 'This user name is already taken'
        }));
      }
    } catch (error) {
      console.error('Error checking user name  uniqueness:', error);
    }
  };

  const handleEmailBlur = () => {
    if (!isLogin && formData.email) {
      checkEmailUniqueness(formData.email);
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
          {isLogin ? 'Login to Your Account' : 'Create an Account'}
        </h2>
        
        {/* Server message display */}
        {serverMessage.text && (
          <div className={`server-message ${serverMessage.type}`}>
            {serverMessage.text}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          {/* Name field (signup only) */}
          {!isLogin && (
            <div className="form-group">
              <label className="form-label" htmlFor="name">
                User Name
              </label>
              <input
                id="name"
                name="name"
                type="text"
                value={formData.name}
                onChange={handleChange}
                className={errors.name ? 'form-input error' : 'form-input'}
                placeholder="Enter your unique user name"
              />
              {errors.name && <p className="error-message">{errors.name}</p>}
            </div>
          )}
          
          {/* Email field */}
          <div className="form-group">
            <label className="form-label" htmlFor="email">
              Email Address
            </label>
            <input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              onBlur={handleEmailBlur}
              className={errors.email ? 'form-input error' : 'form-input'}
              placeholder="Enter your email"
            />
            {errors.email && <p className="error-message">{errors.email}</p>}
          </div>
          
          {/* Password field */}
          <div className="form-group">
            <label className="form-label" htmlFor="password">
              Password
            </label>
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
          
          {/* Confirm Password field (signup only) */}
          {!isLogin && (
            <div className="form-group">
              <label className="form-label" htmlFor="confirmPassword">
                Confirm Password
              </label>
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
          
          {/* Submit button */}
          <div className="form-group">
            <button
              type="submit"
              className="submit-button"
              disabled={isLoading}
            >
              {isLoading ? (
                <span className="loading-spinner"></span>
              ) : (
                isLogin ? 'Login' : 'Sign Up'
              )}
            </button>
          </div>
          
          {/* Forgot password (login only) */}
          {isLogin && (
            <div className="forgot-password">
              <a href="#" className="forgot-password-link">
                Forgot your password?
              </a>
            </div>
          )}
          
          {/* Toggle between login and signup */}
          <div className="auth-switch">
            <p>
              {isLogin ? "Don't have an account? " : "Already have an account? "}
              <button
                type="button"
                onClick={toggleAuthMode}
                className="switch-button"
              >
                {isLogin ? 'Sign up' : 'Login'}
              </button>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};
