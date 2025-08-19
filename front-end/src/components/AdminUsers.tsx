// src/components/AdminUsers.tsx

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';
import api from '../services/api';
import Sidebar from './Sidebar';
import { IDecodedUserToken, IUser } from '../types'; // Importa las interfaces necesarias

const AdminUsers: React.FC = () => { // Tipamos el componente
    // Tipamos el estado 'users' como un array de IUser
    const [users, setUsers] = useState<IUser[]>([]);
    const [message] = useState<string>(''); // Tipamos el estado como string
    const [error, setError] = useState<string>(''); // Tipamos el estado como string
    // Tipamos el estado 'user' como IDecodedUserToken o null
    const [user, setUser] = useState<IDecodedUserToken | null>(null);
    const navigate = useNavigate();

    //  para obtener el token y decodificar la información del usuario
    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (token) {
            try {
                // Tipamos la decodificación del token
                const decodedToken: IDecodedUserToken = jwtDecode(token);
                setUser(decodedToken);
            } catch (error) {
                console.error("Error decoding token:", error);
                localStorage.removeItem('access_token');
                navigate('/');
            }
        }
    }, [navigate]);

    //  para obtener todos los usuarios del backend
    const fetchAllUsers = async () => {
        try {
            // Tipamos la respuesta esperada de la API
            const response = await api.get<{ users: IUser[] }>('/users/');
            setUsers(response.data.users);
        } catch (err: any) { // Tipamos el error como any
            setError('No tienes permisos para ver esta página o hubo un error.');
        }
    };

    // Efecto para llamar a la API cuando el usuario se ha cargado y es admin
    useEffect(() => {
        if (user && user.role === 'admin') { // Aseguramos que solo los admins puedan buscar usuarios
            fetchAllUsers();
        } else if (user && user.role !== 'admin') {
            setError('Acceso denegado: esta página es solo para administradores.');
            
        }
    }, [user, navigate]); 

    // Manejo de estados de carga y error
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
                <div className="users-table-container">
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
                            {/* Aseguramos que userItem sea de tipo IUser */}
                            {users.map((userItem: IUser) => (
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