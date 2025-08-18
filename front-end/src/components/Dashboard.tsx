// src/components/Dashboard.tsx

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';
import Sidebar from './Sidebar';
import { IDecodedUserToken } from '../types';

const Dashboard: React.FC = () => {
    // Type 'user' as IDecodedUserToken or null
    const [user, setUser] = useState<IDecodedUserToken | null>(null);
    // Type 'isLoading' as boolean
    const [isLoading, setIsLoading] = useState<boolean>(true); 
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (token) {
            try {
                // Type the decoded token
                const decodedToken: IDecodedUserToken = jwtDecode(token);
                setUser(decodedToken);
            } catch (error) {
                console.error("Error decoding token:", error);
                localStorage.removeItem('access_token');
                navigate('/');
            }
        }
        setIsLoading(false);
    }, [navigate]);

    if (isLoading) {
        return <div>Cargando...</div>;
    }

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