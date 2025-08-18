// src/components/Users.tsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';
import api from '../services/api';
import Sidebar from './Sidebar';
import { IDecodedUserToken, IUser } from '../types'; 

const Users: React.FC = () => { // Tipamos el componente como React.FC
    // Tipamos 'lockedUsers' como un array de IUser
    const [lockedUsers, setLockedUsers] = useState<IUser[]>([]);
    // Tipamos 'message' y 'error' como string
    const [message, setMessage] = useState<string>('');
    const [error, setError] = useState<string>('');
    // Tipamos 'user' como IDecodedUserToken o null
    const [user, setUser] = useState<IDecodedUserToken | null>(null);
    const navigate = useNavigate();

    //  Obtener la información del usuario del token al cargar el componente
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

    // Para obtener usuarios bloqueados del backend
    const fetchLockedUsers = async () => {
        try {
            // Tipamos la respuesta esperada: un array de IUser
            const response = await api.get<IUser[]>('/admin/locked-users');
            setLockedUsers(response.data);
            if (response.data.length === 0) {
                setMessage('No hay usuarios bloqueados.');
            }
        } catch (err: any) { 
            setError('No tienes permisos para ver esta página.');
        }
    };

    // Para desbloquear a un usuario
    const unlockUser = async (userId: number) => { // Tipamos userId como number
        try {
            await api.put(`/admin/users/${userId}/unlock`);
            setMessage('Usuario desbloqueado con éxito.');
            // Vuelve a cargar la lista después de desbloquear
            fetchLockedUsers();
        } catch (err: any) { // Any para capturar errores
            setError('Ocurrió un error al intentar desbloquear al usuario.');
        }
    };

    // Cargar la lista de usuarios cuando el componente se monta o cuando el usuario (admin) se carga
    useEffect(() => {
        // Solo cargar si el usuario está disponible y es un admin
        if (user && user.role === 'admin') {
            fetchLockedUsers();
        } else if (user && user.role !== 'admin') {
            // Manejar si un usuario que no sea admin al intentar acceder
            setError('Acceso denegado: esta página es solo para administradores.');
        }
    }, [user, navigate]); // Se utiliza 'navigate' para redirigir si es necesario

    // Manejo de estados de carga y error
    if (error) {
        return <div className="error-message">{error}</div>;
    }
    
    // Si el usuario no se ha cargado aún, muestra un mensaje de carga.
    if (!user) {
      return <div>Cargando...</div>;
    }

    // Para la renderización
    return (
        <div className="app-layout">
            <Sidebar user={user} />
            <main className="content">
                <div className="users-table-container"> 
                    <h2>Usuarios Bloqueados</h2>
                    {message && <p className="info-message">{message}</p>}
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Nombre</th>
                                <th>Email</th>
                                <th>Acción</th>
                            </tr>
                        </thead>
                        <tbody>
                            {/* Tipamos userItem como IUser */}
                            {lockedUsers.map((userItem: IUser) => (
                                <tr key={userItem.id}>
                                    <td>{userItem.id}</td>
                                    <td>{userItem.name}</td>
                                    <td>{userItem.email}</td>
                                    <td>
                                        <button onClick={() => unlockUser(userItem.id)}>
                                            Desbloquear
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </main>
        </div>
    );
};

export default Users;