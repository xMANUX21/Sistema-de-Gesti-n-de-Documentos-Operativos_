import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { resetPassword } from '../services/api';

const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [token, setToken] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    // Lee el token de la URL automáticamente al cargar el componente
    const urlToken = searchParams.get('token');
    if (urlToken) {
      setToken(urlToken);
    } else {
      setError('Token no encontrado en la URL. El enlace es inválido.');
    }
  }, [searchParams]);

const handleResetPassword = async (e) => {
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
  } catch (err) {
    // Manejo de errores 
    let errorMessage = 'Ocurrió un error al intentar cambiar la contraseña.';
    
    // Si la respuesta del backend tiene un detalle, se extrae
    if (err.response && err.response.data && err.response.data.detail) {
      const errorDetail = err.response.data.detail;
      
      if (typeof errorDetail === 'string') {
        // Es un  mensaje de error (
        errorMessage = errorDetail;
      } else if (Array.isArray(errorDetail) && errorDetail.length > 0) {
        // Es un error de validación, extraemos el primer mensaje
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
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <div>
            <label>Confirmar Contraseña:</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
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