import React, { useEffect, useState } from "react";
import Layout from "../components/layout";
import api from "../api/client";

export default function ImportPage() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [imports, setImports] = useState([]);

  const loadImports = async () => {
    try {
      const { data } = await api.get("/dashboard/imports");
      setImports(data);
    } catch (err) {
      setMessage("Erro ao carregar histórico de importações.");
    }
  };

  useEffect(() => {
    loadImports();
  }, []);

  const handleUpload = async (e) => {
    e.preventDefault();
    setMessage("");

    if (!file) {
      setMessage("Selecione um arquivo Excel.");
      return;
    }

    const formData = new FormData();
    formData.append("arquivo", file);

    try {
      const { data } = await api.post("/imports/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setMessage(data.message);
      setFile(null);
      await loadImports();
    } catch (err) {
      setMessage(err?.response?.data?.detail || "Erro no upload.");
    }
  };

  return (
    <Layout>
      <h1>Importar planilha Excel</h1>

      <div className="card">
        <form onSubmit={handleUpload}>
          <input
            type="file"
            accept=".xlsx,.xls"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
          <button type="submit">Enviar arquivo</button>
        </form>

        {message && <p>{message}</p>}
      </div>

      <div className="card">
        <h2>Histórico de importações</h2>

        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Arquivo</th>
              <th>Usuário</th>
              <th>Status</th>
              <th>Observação</th>
            </tr>
          </thead>
          <tbody>
            {imports.map((item) => (
              <tr key={item.id}>
                <td>{item.id}</td>
                <td>{item.nome_arquivo}</td>
                <td>{item.usuario_nome}</td>
                <td>{item.status}</td>
                <td>{item.observacao}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Layout>
  );
}