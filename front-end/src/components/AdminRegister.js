import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';
import api from '../services/api';
import Sidebar from './Sidebar';

const AdminRegister = () => {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        department: '',
        role: 'operador'
    });
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [user, setUser] = useState(null);
    const navigate = useNavigate();

    // Obtener la información del usuario para el Sidebar
    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (token) {
            try {
                const decodedToken = jwtDecode(token);
                setUser(decodedToken);
            } catch (error) {
                localStorage.removeItem('access_token');
                navigate('/');
            }
        }
    }, [navigate]);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');
        setError('');

        try {
            await api.post('/auth/register', formData);
            setMessage('Usuario registrado con éxito.');
            setFormData({ name: '', email: '', password: '', department: '', role: 'operador' });
        } catch (err) {
            if (err.response && err.response.data && err.response.data.detail) {
                setError(err.response.data.detail);
            } else {
                setError('Ocurrió un error al registrar el usuario.');
            }
        }
    };

    if (error) {
        return <div className="error-message">{error}</div>;
    }
    
    if (!user) {
        return <div>Cargando...</div>;
    }

    return (
    <div className="app-layout">
        <Sidebar user={user} />
        <main className="content">
            {/*  la clase  principal del formulario */}
            <div className="register-form-container">
                <h2>Registrar Nuevo Usuario</h2>
                <form onSubmit={handleSubmit}>
                    <div>
                        <label>Nombre:</label>
                        <input type="text" name="name" value={formData.name} onChange={handleChange} required />
                    </div>
                    <div>
                        <label>Email:</label>
                        <input type="email" name="email" value={formData.email} onChange={handleChange} required />
                    </div>
                    <div>
                        <label>Contraseña:</label>
                        <input type="password" name="password" value={formData.password} onChange={handleChange} required />
                    </div>
                    <div>
                        <label>Departamento:</label>
                        <input type="text" name="department" value={formData.department} onChange={handleChange} required />
                    </div>

                    <button type="submit">Registrar</button>
                </form>
                {message && <p className="success-message">{message}</p>}
                {error && <p className="error-message">{error}</p>}
            </div>
        </main>
    </div>
);
};

export default AdminRegister;