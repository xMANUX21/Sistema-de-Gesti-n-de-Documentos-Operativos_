// src/services/api.ts

import axios, { AxiosResponse } from 'axios';
import { ILoginResponse, IUser, IDocument, IDocumentTable, UserRole } from '../types';

const api = axios.create({
  baseURL: 'http://localhost:8000/api', // Esta URL debe ser del backend
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token a todas las peticiones
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

// ==================== AUTH ====================

// La función 'login' debe retornar un Promise que resuelve a una respuesta de Axios con el tipo ILoginResponse
export const login = (email: string, password: string): Promise<AxiosResponse<ILoginResponse>> =>
  api.post('/auth/login', { email, password });

export const register = (userData: Omit<IUser, 'id' | 'failed_attempts' | 'is_locked'>) => // Tipos para los datos de registro
  api.post('/auth/register', userData);

export const forgotPassword = (email: string): Promise<AxiosResponse<any>> => 
  api.post('/auth/forgot-password', { email });

export const resetPassword = (token: string, password: string): Promise<AxiosResponse<any>> =>
  api.post('/auth/reset-password', { token, password: password });


/* ================= DOCUMENTS ================= */
// Subir PDF
export const uploadDocument = (
  formData: FormData
): Promise<AxiosResponse<{ document_id: number; tables_count: number }>> =>
  api.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

// Lista de documentos + email del usuario logueado
export const getDocuments = (): Promise<
  AxiosResponse<{
    documentos: IDocument[];
    current_user_email: string;
    current_user_role: UserRole;
  }>
> => api.get('/documents');

// Detalle de un documento
export const getDocumentById = (
  id: number
): Promise<AxiosResponse<IDocument>> => api.get(`/documents/${id}`);

// Eliminar documento
export const deleteDocument = (
  id: number
): Promise<AxiosResponse<{ message: string }>> =>
  api.delete(`/documents/${id}`);

/* ================= TABLES ================= */
// Tablas por documento
export const getTablesByDocumentId = (
  documentId: number
): Promise<AxiosResponse<{ items: IDocumentTable[] }>> =>
  api.get(`/tables/${documentId}`);

// Contenido de una tabla específica
export const getTableContent = (
  documentId: number,
  tableUid: string
): Promise<AxiosResponse<IDocumentTable>> =>
  api.get(`/tables/${documentId}/${tableUid}`);

// Búsqueda en tablas
export const searchTables = (
  query: string
): Promise<AxiosResponse<{ results: any[] }>> =>
  api.get(`/tables/search`, { params: { q: query } });

export default api;