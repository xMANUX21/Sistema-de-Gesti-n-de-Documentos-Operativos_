// src/components/Dashboard.js

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';
import Sidebar from './Sidebar';

const Dashboard = () => {
    const [user, setUser] = useState(null);
    const [isLoading, setIsLoading] = useState(true); 
    const navigate = useNavigate();

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
        setIsLoading(false); // <--- Finaliza el estado de carga
    }, [navigate]);

    // Muestra un mensaje de carga mientras se decodifica el token
    if (isLoading) {
        return <div>Cargando...</div>;
    }

    // Si no hay token, redirige al login
    if (!user) {
        return <div>No autorizado. Redirigiendo...</div>;
    }

    return (
        <div className="app-layout">
            <Sidebar user={user} />
            <main className="content">
                <div>
                    <h2>Bienvenido, {user.name}!</h2>
                    <p>Tu rol es: {user.role}</p>
                    <p>Has iniciado sesión con éxito.</p>
                </div>
            </main>
        </div>
    );
};

export default Dashboard;