import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api', //  esta URL debe ser la del backend
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

export const login = (email, password) => api.post('/auth/login', { email, password });
export const register = (userData) => api.post('/auth/register', userData);
export const forgotPassword = (email) => api.post('/auth/forgot-password', { email });
export const resetPassword = (token, password) => api.post('/auth/reset-password', { token, password: password });

// ==================== DOCUMENTS ====================

// Subir documento PDF
export const uploadDocument = (formData) =>
  api.post("/documents/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

// Obtener todos los documentos
export const getDocuments = () => api.get("/documents");

// Obtener un documento por ID
export const getDocumentById = (id) => api.get(`/documents/${id}`);

// Eliminar un documento por ID
export const deleteDocument = (id) => api.delete(`/documents/${id}`);

// ==================== TABLES ====================

// Obtener tablas por ID de documento
export const getTablesByDocumentId = (documentId) =>
  api.get(`/tables/${documentId}`);

// Obtener contenido de una tabla específica
export const getTableContent = (documentId, tableUid) =>
  api.get(`/tables/${documentId}/${tableUid}`);

// Buscar en todas las tablas
export const searchTables = (query) =>
  api.get(`/tables/search?q=${encodeURIComponent(query)}`);

export default api;