import React, { useState } from "react";
import api from "../services/api";

const UploadDocument = () => {
  const [file, setFile] = useState(null);
  const [customName, setCustomName] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      alert("Por favor selecciona un archivo PDF");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("custom_name", customName); // nombre opcional

    try {
      const res = await api.post("/documents/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      alert("Documento subido correctamente: ID " + res.data.document_id);
    } catch (err) {
      console.error(err);
      alert("Error subiendo el documento");
    }
  };

  return (
    <div>
      <h2>Subir Documento PDF</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Nombre personalizado:</label>
          <input
            type="text"
            value={customName}
            onChange={(e) => setCustomName(e.target.value)}
            placeholder="Opcional"
          />
        </div>
        <div>
          <label>Archivo PDF:</label>
          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => setFile(e.target.files[0])}
          />
        </div>
        <button type="submit">Subir</button>
      </form>
    </div>
  );
};

export default UploadDocument;
