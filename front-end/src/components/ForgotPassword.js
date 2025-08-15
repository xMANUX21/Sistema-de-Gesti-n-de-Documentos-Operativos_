import React, { useState } from 'react';
import { forgotPassword } from '../services/api';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');
    
    try {
      await forgotPassword(email);
      setMessage('Si el email existe, se ha enviado un enlace para restablecer la contraseña.');
    } catch (err) {
      // Manejamos el error de forma segura, mostrando el mismo mensaje para no revelar emails válidos.
      setMessage('Si el email existe, se ha enviado un enlace para restablecer la contraseña.');
    }
  };

  return (
    <div className="form-container">
      <h2>¿Olvidaste tu contraseña?</h2>
      <p>Introduce tu email para recibir un enlace de reseteo.</p>
      <form onSubmit={handleForgotPassword}>
        <div>
          <label>Email:</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <button type="submit">Enviar enlace</button>
      </form>
      {message && <p className="success-message">{message}</p>}
      {error && <p className="error-message">{error}</p>}
    </div>
  );
};

export default ForgotPassword;