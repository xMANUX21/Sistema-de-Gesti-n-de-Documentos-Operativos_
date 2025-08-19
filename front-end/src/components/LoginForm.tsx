// src/components/LoginForm.tsx

import React, { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../services/api';
// import { ILoginResponse } from '../types'; //  Importamos la interfaz centralizada

const LoginForm: React.FC = () => {
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState<string>('');
  const navigate = useNavigate();

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      // Usamos ILoginResponse para tipar la respuesta
      const response = await login(email, password);
      const token: string = response.data.access_token;
      
      localStorage.setItem('access_token', token);
      
      navigate('/dashboard'); 
    } catch (err: any) {
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
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Contraseña:</label>
          <input
            type="password"
            value={password}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
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