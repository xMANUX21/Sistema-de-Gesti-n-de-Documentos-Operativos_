import React, { useState, useEffect } from "react";
import api, { uploadDocument, getDocuments, getDocumentById, getTablesByDocumentId, searchTables, deleteDocument } from "../services/api";
import Sidebar from "./Sidebar";

const Documents = () => {
  const [documents, setDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [tables, setTables] = useState({});
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [file, setFile] = useState(null);
  const [currentUserRole] = useState("");
  const [confirmDeleteId, setConfirmDeleteId] = useState(null); // Modal confirmación

  useEffect(() => {
    fetchDocuments();
    // getCurrentUserRole();
  }, []);

  // const getCurrentUserRole = async () => {
  //   try {
  //     // const res = await api.get("/auth/me");
  //     setCurrentUserRole(res.data.role);
  //     //aca se guarda el email para comparar
  //     api.defaults.headers.common["user-email"] = res.data.email;
  //   } catch {
  //     // console.error("No se pudo obtener el rol del usuario");
  //   }
  // };

  const fetchDocuments = async () => {
    try {
      const res = await getDocuments();
      setDocuments(res.data.documentos || []);
      // se guarda el email que el backend nos envia
      api.defaults.headers.common["user-email"] = res.data.current_user_email;
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
    try {
      await uploadDocument(formData);
      setSuccessMsg("Documento subido correctamente");
      setFile(null);
      fetchDocuments();
    } catch {
      setError("Error subiendo documento");
    }
  };

  const handleViewDocument = async (id) => {
    try {
      const res = await getDocumentById(id);
      setSelectedDocument(res.data);
    } catch {
      setError("Error obteniendo documento");
    }
  };

  const handleViewTables = async (id) => {
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

  const handleDeleteDocument = async (id) => {
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
      <Sidebar />
      <main className="content">
        <h2>Gestión de Documentos</h2>

        {error && <p style={{ color: "red" }}>{error}</p>}
        {successMsg && <p style={{ color: "green" }}>{successMsg}</p>}

        {/* Subida de PDF */}
        <div style={{ marginBottom: "20px" }}>
          <input type="file" accept="application/pdf" onChange={(e) => setFile(e.target.files[0])} />
          <button onClick={handleUpload}>Subir PDF</button>
        </div>

        {/* Lista de documentos */}
        <h3>Documentos</h3>
        <table border="1" cellPadding="5">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              {currentUserRole === "admin" && <th>Departamento</th>}
              <th>Subido por</th>
              <th>Fecha</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc) => {

              return (
              <tr key={doc.id}>
                <td>{doc.id}</td>
                <td>{doc.nombre}</td>
                {currentUserRole === "admin" && <td>{doc.department}</td>}
                <td>{doc.uploaded_by || "—"}</td>
                <td>{doc.fecha_subida}</td>
                <td>
                  <button onClick={() => handleViewDocument(doc.id)}>Ver Detalle</button>
                  <button onClick={() => handleViewTables(doc.id)}>Ver Tablas</button>
                  { true && (
                    <button
                      style={{ backgroundColor: "red", color: "white", marginLeft: "5px" }}
                      onClick={() => setConfirmDeleteId(doc.id)}
                    >
                      Eliminar
                    </button>
                  )}
                </td>
              </tr>
              );
            })}
          </tbody>
        </table>

        {/* Detalle del documento */}
        {selectedDocument && (
          <div style={{ marginTop: "20px", border: "1px solid #ccc", padding: "10px" }}>
            <h3>Detalle del Documento</h3>
            <p><b>ID:</b> {selectedDocument.id}</p>
            <p><b>Nombre:</b> {selectedDocument.nombre}</p>
            <p><b>Fecha:</b> {selectedDocument.fecha_subida}</p>
            <p><b>Departamento:</b> {selectedDocument.department}</p>
            <p><b>Subido por:</b> {selectedDocument.uploaded_by || "—"}</p>
            <button onClick={() => setSelectedDocument(null)}>Cerrar</button>
          </div>
        )}

        {/* Tablas por documento */}
        {Object.keys(tables).map((docId) => (
          <div key={docId} style={{ marginTop: "20px" }}>
            <h4>Tablas del Documento {docId}</h4>
            <ul>
              {tables[docId].map((t) => (
                <li key={t.id}>
                  {t.name} - Página {t.page}
                </li>
              ))}
            </ul>
          </div>
        ))}

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
                <table border="1" cellPadding="5" style={{ borderCollapse: "collapse", width: "100%" }}>
                  <thead>
                    <tr>
                      {res.headers.map((header, hIdx) => (
                        <th key={hIdx}>{header}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {res.rows.map((row, rIdx) => (
                      <tr key={rIdx}>
                        {row.map((cell, cIdx) => (
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

        {/* Modal de confirmación */}
        {confirmDeleteId && (
          <div style={{
            position: "fixed",
            top: 0, left: 0, width: "100%", height: "100%",
            backgroundColor: "rgba(0,0,0,0.5)",
            display: "flex", alignItems: "center", justifyContent: "center",
            zIndex: 1000
          }}>
            <div style={{
              backgroundColor: "white", padding: "20px", borderRadius: "8px",
              width: "350px", textAlign: "center"
            }}>
              <h3>¿Eliminar documento?</h3>
              <p>Esta acción no se puede deshacer.</p>
              <div style={{ marginTop: "20px" }}>
                <button
                  style={{ backgroundColor: "red", color: "white", padding: "5px 10px", marginRight: "10px" }}
                  onClick={() => {
                    handleDeleteDocument(confirmDeleteId);
                    setConfirmDeleteId(null);
                  }}
                >
                  Sí, eliminar
                </button>
                <button
                  style={{ backgroundColor: "gray", color: "white", padding: "5px 10px" }}
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
