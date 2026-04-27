import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";
import api from "../api/client";

export default function ImportPage() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [imports, setImports] = useState([]);
  const [uploadResult, setUploadResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadImports = async () => {
    try {
      const { data } = await api.get("/dashboard/imports");
      setImports(data);
    } catch {
      setMessage("Erro ao carregar histórico de importações.");
    }
  };

  useEffect(() => {
    loadImports();
  }, []);

  const handleUpload = async (e) => {
    e.preventDefault();
    setMessage("");
    setUploadResult(null);

    if (!file) {
      setMessage("Selecione um arquivo Excel.");
      return;
    }

    const formData = new FormData();
    formData.append("arquivo", file);

    try {
      setLoading(true);

      const { data } = await api.post("/imports/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setMessage(data.message);
      setUploadResult(data);
      setFile(null);
      e.target.reset();
      await loadImports();
    } catch (err) {
      setMessage(err?.response?.data?.detail || "Erro no upload.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <h1>Importar planilha Excel</h1>

      <div className="card">
        <h2>Upload e validação automática</h2>

        <p className="hint">
          Colunas esperadas: data_venda, vendedor, regiao, produto, categoria,
          quantidade, valor_unitario e valor_total.
        </p>

        <form onSubmit={handleUpload}>
          <input
            type="file"
            accept=".xlsx,.xls"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />

          <button type="submit" disabled={loading}>
            {loading ? "Processando..." : "Enviar arquivo"}
          </button>
        </form>

        {message && (
          <p className={message.includes("Erro") ? "error" : "success"}>
            {message}
          </p>
        )}
      </div>

      {uploadResult && (
        <div className="card">
          <h2>Resumo do processamento</h2>

          <div className="grid">
            <div className="stat">
              <span>Total de registros</span>
              <p>{uploadResult.total_registros}</p>
            </div>

            <div className="stat">
              <span>Registros válidos</span>
              <p>{uploadResult.total_validos}</p>
            </div>

            <div className="stat">
              <span>Registros inválidos</span>
              <p>{uploadResult.total_invalidos}</p>
            </div>
          </div>

          {uploadResult.registros_invalidos?.length > 0 && (
            <div className="validation-box">
              <h3>Inconsistências encontradas</h3>

              <table>
                <thead>
                  <tr>
                    <th>Linha</th>
                    <th>Produto</th>
                    <th>Erros</th>
                  </tr>
                </thead>

                <tbody>
                  {uploadResult.registros_invalidos.map((item) => (
                    <tr key={item.linha}>
                      <td>{item.linha}</td>
                      <td>{item.produto || "-"}</td>
                      <td>{item.erros.join(", ")}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

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