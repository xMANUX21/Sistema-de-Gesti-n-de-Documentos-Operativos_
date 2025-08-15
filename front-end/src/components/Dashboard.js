import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from './Sidebar';
import { jwtDecode } from 'jwt-decode';

const Dashboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);

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

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    navigate('/');
  };

  if (!user) {
    return <div>Cargando...</div>;
  }

  return (
    <div className="app-layout">
      <Sidebar user={user} />
      <main className="content">
        <h2>Bienvenido, {user.name}!</h2>
        <p>Tu rol es: {user.role}</p>
        <p>Has iniciado sesión con éxito.</p>
       
        <button onClick={handleLogout}>Cerrar Sesión</button> 
      </main>
    </div>
  );
};

export default Dashboard;