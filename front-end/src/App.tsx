// src/App.tsx

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginForm from './components/LoginForm';
import ForgotPassword from './components/ForgotPassword';
import ResetPassword from './components/ResetPassword';
import Dashboard from './components/Dashboard';
import ProtectedRoute from './components/ProtectedRoute';
import Users from './components/Users';
import AdminRegister from './components/AdminRegister'; 
import AdminUsers from './components/AdminUsers';
import Documents from './components/Documents';

// Importa el archivo de estilos CSS
import './App.css'; 

const App: React.FC = () => { // Se usa React.FC para tipar el componente funcional
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginForm />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        
        {/* Rutas protegidas */}
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } 
        />
        
        {/* Ruta para Usuarios Bloqueados */}
        <Route 
          path="/admin/users" 
          element={
            <ProtectedRoute>
              <Users />
            </ProtectedRoute>
          } 
        />

        {/* Ruta para el registro de usuarios por el administrador */}
        <Route 
          path="/admin/register" 
          element={
            <ProtectedRoute>
              <AdminRegister />
            </ProtectedRoute>
          } 
        />
        
        {/* Ruta para la gestión de todos los usuarios */}
        <Route 
          path="/admin/all-users" 
          element={
            <ProtectedRoute>
              <AdminUsers />
            </ProtectedRoute>
          } 
        />

        {/* Subida de los Documentos PDF*/}
        <Route
          path='/documents/upload'
          element={
            <ProtectedRoute>
              <Documents />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
};

export default App;