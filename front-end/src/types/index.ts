// src/types/index.ts

// Utilidad para los roles, si los roles cambian
export type UserRole = 'admin' | 'operador';

// Interfaces para la autenticación y la información del usuario
export interface ILoginResponse {
  access_token: string;
  token_type: string;
  // El backend puede devolver directamente el role del usuario.
  role: UserRole;
}

export interface IDecodedUserToken {
  sub: string; // ID del usuario
  role: UserRole;
  email: string;
  name: string;
  exp: number; // Timestamp de expiración del token.
}

// Interfaz para los datos de usuario completos obtenidos de los endpoints de admin
export interface IUser {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  department?: string; //  este campo es opcional.
  failed_attempts: number;
  is_locked: boolean;
}

// Interfaz para los datos de usuario que se envían al backend para registro.
// Con el Omit crea un nuevo tipo sin los campos que el backend genera automáticamente.
export type IRegisterUser = Omit<IUser, 'id' | 'failed_attempts' | 'is_locked'>;

export interface IAdminRegisterForm extends IRegisterUser {
    password: string;
}

// Interfaces para los documentos
export interface IDocument {
  id: number;
  nombre: string;
  contenido: string;
  fecha_subida: string; // String en formato '2025-08-18T22:30:00.000Z'
  department: string;
  uploaded_by: string;
}

// Interfaces para las tablas dentro de los documentos
export interface IDocumentTable {
  id: number;
  document_id: number;
  table_uid: string;
  page: number;
  bbox: string; // 'bbox' es un JSON string.
  n_rows: number;
  n_cols: number;
  detection: string;
  confidence: number;
  title_guess?: string; 
  headers?: any; // JSON, puede ser un array de strings. Se usa el any si la estructura es flexible.
  rows_data?: any; // JSON, puede ser un array de arrays. Se usa con any si la estructura es flexible.
}