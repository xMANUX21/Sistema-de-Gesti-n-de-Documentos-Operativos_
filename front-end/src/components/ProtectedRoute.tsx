// src/components/ProtectedRoute.tsx
import React from 'react';
import { Navigate } from 'react-router-dom';

// Define la interfaz para las props del componente ProtectedRoute
interface ProtectedRouteProps {
  children: React.ReactNode; // Con children puede ser cualquier cosa que React pueda renderizar
}

// Usamos React.FC con la interfaz de props definida
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const token = localStorage.getItem('access_token');

  if (!token) {
    // Si no hay un token, redirige al login
    return <Navigate to="/" replace />;
  }

  // Si hay un token, renderiza los componentes hijos
  return <>{children}</>; // Usamos un React Fragment para envolver children
};

export default ProtectedRoute;