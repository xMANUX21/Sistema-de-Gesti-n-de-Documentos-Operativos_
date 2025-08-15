import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';
import api from '../services/api';
import Sidebar from './Sidebar';

const Users = () => {
    const [lockedUsers, setLockedUsers] = useState([]);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [user, setUser] = useState(null); // Estado para la información del usuario
    const navigate = useNavigate();

    // 1. Obtener la información del usuario del token al cargar el componente
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

    // Para obtener usuarios bloqueados del backend
    const fetchLockedUsers = async () => {
        try {
            const response = await api.get('/admin/locked-users');
            setLockedUsers(response.data);
            if (response.data.length === 0) {
                setMessage('No hay usuarios bloqueados.');
            }
        } catch (err) {
            setError('No tienes permisos para ver esta página.');
        }
    };

    // Para desbloquear a un usuario
    const unlockUser = async (userId) => {
        try {
            await api.put(`/admin/users/${userId}/unlock`);
            setMessage('Usuario desbloqueado con éxito.');
            // Vuelve a cargar la lista 
            fetchLockedUsers();
        } catch (err) {
            setError('Ocurrió un error al intentar desbloquear al usuario.');
        }
    };

    // 4. Cargar la lista de usuarios cuando el componente se monta
    useEffect(() => {
        fetchLockedUsers();
    }, []);

    //  Manejo de estados de carga y error
    if (error) {
        return <div className="error-message">{error}</div>;
    }
    
    // Si el usuario no se ha cargado aun
    if (!user) {
      return <div>Cargando...</div>;
    }

    // Para la renderización
    return (
        <div className="app-layout">
            <Sidebar user={user} />
            <main className="content">
                <div className="users-container">
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
                            {lockedUsers.map(userItem => (
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