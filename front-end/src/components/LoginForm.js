import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../services/api';

const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await login(email, password);
      const token = response.data.access_token;
      
      // Guarda el token en el almacenamiento local
      localStorage.setItem('access_token', token);
      
      // Redirige al usuario a la página principal
      navigate('/dashboard'); 
    } catch (err) {
      // Manejo de errores
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Ocurrió un error al intentar iniciar sesión.');
      }
    }
  };

  return (
    <div className="login-container">
      <h2>Iniciar Sesión</h2>
      <form onSubmit={handleLogin}>
        <div>
          <label>Email:</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Contraseña:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit">Entrar</button>
      </form>
      {error && <p className="error-message">{error}</p>}
      <p>
        <a href="/forgot-password">¿Olvidaste tu contraseña?</a>
      </p>
    </div>
  );
};

export default LoginForm;