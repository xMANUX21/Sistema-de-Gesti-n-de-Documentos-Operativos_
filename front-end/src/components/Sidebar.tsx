// src/components/Sidebar.tsx

import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { IDecodedUserToken } from '../types';

// Define los props que el componente Sidebar recibirá
interface SidebarProps {
  user: IDecodedUserToken | null; // Puede ser null si no hay usuario
}

// Use React.FC with the defined props interface
const Sidebar: React.FC<SidebarProps> = ({ user }) => {
  const navigate = useNavigate();
  
  const handleLogout = () => {
    localStorage.removeItem('access_token');
    navigate('/');
  };

  // Revisa si el role es admin
  const isAdmin = user && user.role === 'admin';

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h3>Menú</h3>
      </div>
      <nav className="sidebar-nav">
        <ul>
          <li>
            <Link to="/dashboard">Dashboard</Link>
          </li>
          <li>
            <Link to="/documents/upload">Documentos</Link>
          </li>
          {isAdmin && (
            <>
              <li>
                <Link to="/admin/all-users">Usuarios</Link>
              </li>
              <li>
                <Link to="/admin/register">Registrar Usuario</Link>
              </li>
              <li>
                <Link to="/admin/users">Usuarios Bloqueados</Link>
              </li>
            </>
          )}
          <button onClick={handleLogout}>Cerrar Sesión</button>
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;