// src/components/Documents.tsx
import React, { useState, useEffect } from "react";
import {jwtDecode} from "jwt-decode";
import api, {
  getDocuments,
  getDocumentById,
  getTablesByDocumentId,
  searchTables,
  deleteDocument,
} from "../services/api";
import Sidebar from "./Sidebar";
import { IDocument, IDocumentTable, IDecodedUserToken } from "../types";

const Documents: React.FC = () => {
  const [documents, setDocuments] = useState<IDocument[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<IDocument | null>(null);
  const [tables, setTables] = useState<Record<number, IDocumentTable[]>>({});
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [error, setError] = useState<string>("");
  const [successMsg, setSuccessMsg] = useState<string>("");
  const [file, setFile] = useState<File | null>(null);
  const [user, setUser] = useState<IDecodedUserToken | null>(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      const decoded = jwtDecode<IDecodedUserToken>(token);
      setUser(decoded);
      api.defaults.headers.common["user-email"] = decoded.email;
    }
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const res = await getDocuments();
      setDocuments(res.data.documentos || []);
    } catch {
      setError("Error cargando documentos");
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Selecciona un archivo PDF");
      return;
    }
    const formData = new FormData();
    formData.append("file", file);
    const token = localStorage.getItem("access_token");
  if (!token) {
    setError("No estás autenticado");
    return;
  }

  try {
    await api.post("/documents/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
        Authorization: `Bearer ${token}`,
      },
    });
    setSuccessMsg("Documento subido correctamente");
    setFile(null);
    fetchDocuments();
  } catch (err: any) {
    console.error(err);
    setError("Error subiendo documento, solo se permiten PDFs");
  }
};

  const handleViewDocument = async (id: number) => {
    try {
      const res = await getDocumentById(id);
      setSelectedDocument(res.data);
    } catch {
      setError("Error obteniendo documento");
    }
  };

  const handleViewTables = async (id: number) => {
    if (tables[id]) {
      const updated = { ...tables };
      delete updated[id];
      setTables(updated);
      return;
    }
    try {
      const res = await getTablesByDocumentId(id);
      setTables((prev) => ({ ...prev, [id]: res.data.items || [] }));
    } catch {
      setError("Error obteniendo tablas");
    }
  };

  const handleSearchTables = async () => {
    if (!searchQuery) return;
    try {
      const res = await searchTables(searchQuery);
      setSearchResults(res.data.results || []);
    } catch {
      setError("No se encontraron resultados");
      setSearchResults([]);
    }
  };

  const handleDeleteDocument = async (id: number) => {
    try {
      await deleteDocument(id);
      setSuccessMsg("Documento eliminado correctamente");
      fetchDocuments();
    } catch {
      setError("Error eliminando documento");
    }
  };

  return (
    <div className="app-layout">
      <Sidebar user={user} />
      <main className="content">
        <h2>Gestión de Documentos</h2>
        {error && <p style={{ color: "red" }}>{error}</p>}
        {successMsg && <p style={{ color: "green" }}>{successMsg}</p>}

        <div style={{ marginBottom: "20px" }}>
          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
          <button onClick={handleUpload}>Subir PDF</button>
        </div>

        <h3>Documentos</h3>
        <table border={1} cellPadding={5}>
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              {user?.role === "admin" && <th>Departamento</th>}
              <th>Subido por</th>
              <th>Fecha</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc) => (
              <tr key={doc.id}>
                <td>{doc.id}</td>
                <td>{doc.nombre}</td>
                {user?.role === "admin" && <td>{doc.department}</td>}
                <td>{doc.uploaded_by}</td>
                <td>{doc.fecha_subida}</td>
                <td>
                  <button onClick={() => handleViewDocument(doc.id)}>Ver Detalle</button>
                  <button onClick={() => handleViewTables(doc.id)}>Ver Tablas</button>
                  {(user?.role === "admin" || doc.uploaded_by === user?.email) && (
                    <button
                      style={{ backgroundColor: "red", color: "white", marginLeft: 5 }}
                      onClick={() => setConfirmDeleteId(doc.id)}
                    >
                      Eliminar
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {selectedDocument && (
          <div style={{ marginTop: 20, border: "1px solid #ccc", padding: 10 }}>
            <h3>Detalle del Documento</h3>
            <p><b>ID:</b> {selectedDocument.id}</p>
            <p><b>Nombre:</b> {selectedDocument.nombre}</p>
            <p><b>Fecha:</b> {selectedDocument.fecha_subida}</p>
            <p><b>Departamento:</b> {selectedDocument.department}</p>
            <p><b>Subido por:</b> {selectedDocument.uploaded_by}</p>
            <button onClick={() => setSelectedDocument(null)}>Cerrar</button>
          </div>
        )}

        {/* Tablas por documento */}
        {Object.keys(tables).map((docIdStr) => {
          const docId = Number(docIdStr);
          return (
            <div key={docId} style={{ marginTop: "20px" }}>
              <h4>Tablas del Documento {docId}</h4>
              <ul>
                {tables[docId]?.map((t) => (
                  <li key={t.table_uid}>
                    {t.title_guess || t.table_uid} - Página {t.page}
                  </li>
                ))}
              </ul>
            </div>
          );
        })}

        {/* Buscar en tablas */}
        <h3>Buscar en Tablas</h3>
        <input
          type="text"
          placeholder="Texto a buscar..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <button onClick={handleSearchTables}>Buscar</button>

        {searchResults.length > 0 && (
          <div style={{ marginTop: "20px" }}>
            {searchResults.map((res, idx) => (
              <div key={idx} style={{ border: "1px solid #ccc", padding: "10px", marginBottom: "15px" }}>
                <h4>Documento #{res.document_id} - Tabla {res.table_uid}</h4>
                <p><b>{res.title_guess}</b></p>
                <table style={{ borderCollapse: "collapse", width: "100%" }}>
                  <thead>
                    <tr>
                      {(res.headers as string[]).map((header: string, hIdx: number) => (
                        <th key={hIdx}>{header}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {(res.rows as string[][]).map((row: string[], rIdx: number) => (
                      <tr key={rIdx}>
                        {row.map((cell: string, cIdx: number) => (
                          <td key={cIdx}>{cell}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ))}
          </div>
        )}

        {confirmDeleteId && (
          <div
            style={{
              position: "fixed",
              top: 0,
              left: 0,
              width: "100%",
              height: "100%",
              backgroundColor: "rgba(0,0,0,0.5)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              zIndex: 1000,
            }}
          >
            <div
              style={{
                backgroundColor: "white",
                padding: "20px",
                borderRadius: "8px",
                width: "350px",
                textAlign: "center",
              }}
            >
              <h3>¿Eliminar documento?</h3>
              <p>Esta acción no se puede deshacer.</p>
              <div style={{ marginTop: "20px" }}>
                <button
                  style={{
                    backgroundColor: "red",
                    color: "white",
                    padding: "5px 10px",
                    marginRight: "10px",
                  }}
                  onClick={() => {
                    handleDeleteDocument(confirmDeleteId);
                    setConfirmDeleteId(null);
                  }}
                >
                  Sí, eliminar
                </button>
                <button
                  style={{
                    backgroundColor: "gray",
                    color: "white",
                    padding: "5px 10px",
                  }}
                  onClick={() => setConfirmDeleteId(null)}
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default Documents;