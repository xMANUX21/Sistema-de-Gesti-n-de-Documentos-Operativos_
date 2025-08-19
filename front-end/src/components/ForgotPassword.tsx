// src/components/ForgotPassword.tsx

import React, { useState, FormEvent } from 'react';
import { forgotPassword } from '../services/api';

const ForgotPassword: React.FC = () => {
    // Se tipean los estados string
    const [email, setEmail] = useState<string>('');
    const [message, setMessage] = useState<string>('');
    const [error, setError] = useState<string>('');

    // Tipea el evento del formulario
    const handleForgotPassword = async (e: FormEvent) => {
        e.preventDefault();
        setMessage('');
        setError('');
        
        try {
            await forgotPassword(email);
            setMessage('Si el email existe, se ha enviado un enlace para restablecer la contraseña.');
        } catch (err) {
            console.error("Forgot password error:", err);
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
                        // Tipea el evento del input
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
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