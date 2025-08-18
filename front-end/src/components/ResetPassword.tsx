// src/components/ResetPassword.tsx

import React, { useState, useEffect, FormEvent } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { resetPassword } from '../services/api';

const ResetPassword: React.FC = () => {
  const [searchParams] = useSearchParams();
  // Tipea los estados como string
  const [password, setPassword] = useState<string>('');
  const [confirmPassword, setConfirmPassword] = useState<string>('');
  const [token, setToken] = useState<string>('');
  const [message, setMessage] = useState<string>('');
  const [error, setError] = useState<string>('');
  const navigate = useNavigate();

  useEffect(() => {
    const urlToken = searchParams.get('token');
    if (urlToken) {
      setToken(urlToken);
    } else {
      setError('Token no encontrado en la URL. El enlace es inválido.');
    }
  }, [searchParams]);

  // Tipea el evento del formulario
  const handleResetPassword = async (e: FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError('Las contraseñas no coinciden.');
      return;
    }
    
    if (!token) {
      setError('Token inválido o expirado.');
      return;
    }

    try {
      const response = await resetPassword(token, password);
      setMessage(response.data.message);
      setTimeout(() => navigate('/'), 3000); 
    } catch (err: any) {
      let errorMessage = 'Ocurrió un error al intentar cambiar la contraseña.';
      
      if (err.response && err.response.data && err.response.data.detail) {
        const errorDetail = err.response.data.detail;
        
        if (typeof errorDetail === 'string') {
          errorMessage = errorDetail;
        } else if (Array.isArray(errorDetail) && errorDetail.length > 0) {
          errorMessage = errorDetail[0].msg;
        }
      }
      
      setError(errorMessage);
    }
  };

  return (
    <div className="form-container">
      <h2>Restablecer Contraseña</h2>
      {!token ? (
        <p className="error-message">{error}</p>
      ) : (
        <form onSubmit={handleResetPassword}>
          <div>
            <label>Nueva Contraseña:</label>
            <input
              type="password"
              value={password}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
              required
            />
          </div>
          <div>
            <label>Confirmar Contraseña:</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setConfirmPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit">Cambiar Contraseña</button>
        </form>
      )}
      {message && <p className="success-message">{message}</p>}
      {error && <p className="error-message">{error}</p>}
    </div>
  );
};

export default ResetPassword;