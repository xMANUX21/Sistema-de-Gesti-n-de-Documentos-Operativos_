// src/components/AdminUsers.js

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';
import api from '../services/api';
import Sidebar from './Sidebar';

const AdminUsers = () => {
    // Definiciones de estado
    const [users, setUsers] = useState([]);
    const [message] = useState(''); //  lo mantenemos para consistencia
    const [error, setError] = useState('');
    const [user, setUser] = useState(null);
    const navigate = useNavigate();

    //  para obtener el token y decodificar la información del usuario
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

    // para obtener todos los usuarios del backend
    const fetchAllUsers = async () => {
        try {
            const response = await api.get('/users/');
            setUsers(response.data.users);
        } catch (err) {
            setError('No tienes permisos para ver esta página o hubo un error.');
        }
    };

    // para llamar a la API cuando el usuario se ha cargado
    useEffect(() => {
        if (user) {
            fetchAllUsers();
        }
    }, [user]);

    // Manejo de estados de carga y error
    if (error) {
        return <div className="error-message">{error}</div>;
    }
    
    if (!user) {
        return <div>Cargando...</div>;
    }

    //  para renderizar el componente
    return (
        <div className="app-layout">
            <Sidebar user={user} />
            <main className="content">
                <div>
                    <h2>Todos los Usuarios</h2>
                    {message && <p className="info-message">{message}</p>}
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Nombre</th>
                                <th>Email</th>
                                <th>Rol</th>
                                <th>Estado</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map(userItem => (
                                <tr key={userItem.id}>
                                    <td>{userItem.id}</td>
                                    <td>{userItem.name}</td>
                                    <td>{userItem.email}</td>
                                    <td>{userItem.role}</td>
                                    <td>{userItem.is_locked ? 'Bloqueado' : 'Activo'}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </main>
        </div>
    );
};

export default AdminUsers;