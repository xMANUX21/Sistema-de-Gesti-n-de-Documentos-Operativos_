import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('access_token');

  if (!token) {
    // Si no hay un token, redirige a la página de login
    return <Navigate to="/" replace />;
  }

  // Si hay un token, renderiza los componentes hijos
  return children;
};

export default ProtectedRoute;