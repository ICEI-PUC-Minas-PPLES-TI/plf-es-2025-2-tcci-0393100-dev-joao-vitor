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
      setMessage("Erro ao carregar importações.");
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

      const { data } = await api.post(
        "/imports/upload",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setMessage(data.message);
      setUploadResult(data);

      await loadImports();

    } catch (err) {
      setMessage(
        err?.response?.data?.detail ||
        "Erro ao realizar upload."
      );
    } finally {
      setLoading(false);
    }
  };

  const percentualSucesso = uploadResult
    ? Math.round(
        (uploadResult.total_validos /
          uploadResult.total_registros) *
          100
      )
    : 0;

    const exportarResultadoCSV = () => {
  if (!uploadResult) return;

  const linhas = [
    ["Tipo", "Linha", "Produto", "Status", "Confiança", "Erros"],
  ];

  uploadResult.registros_processados?.forEach((item) => {
    linhas.push([
      "Válido",
      "",
      item.produto,
      item.status_cruzamento,
      `${Math.round(item.confianca_cruzamento * 100)}%`,
      "",
    ]);
  });

  uploadResult.registros_invalidos?.forEach((item) => {
    linhas.push([
      "Inválido",
      item.linha,
      item.produto || "",
      "",
      "",
      item.erros.join(" | "),
    ]);
  });

  const csv = linhas.map((linha) => linha.join(";")).join("\n");

  const blob = new Blob([csv], {
    type: "text/csv;charset=utf-8;",
  });

  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");

  link.href = url;
  link.download = "relatorio_importacao.csv";
  link.click();

  URL.revokeObjectURL(url);
};

  return (
    <Layout>
      <div className="page-header">
        <h1>Importação Inteligente</h1>

        <p>
          Upload, validação automática, cruzamento de
          produtos e auditoria de importações.
        </p>
      </div>

      <div className="card">
        <h2>Enviar planilha Excel</h2>

        <form onSubmit={handleUpload}>
          <input
            type="file"
            accept=".xlsx,.xls"
            onChange={(e) =>
              setFile(e.target.files?.[0] || null)
            }
          />

          <button disabled={loading}>
            {loading
              ? "Processando..."
              : "Importar planilha"}
          </button>
        </form>

        {message && (
          <div
            className={
              message.toLowerCase().includes("erro")
                ? "alert error"
                : "alert success"
            }
          >
            {message}
          </div>
        )}
      </div>

      {uploadResult && (
        <div className="card">

          <h2>Resultado da importação</h2>
          <button type="button" onClick={exportarResultadoCSV}>
  Exportar relatório CSV
</button>

          <div className="stats-grid">

            <div className="stat-card">
              <span>Total</span>
              <h3>{uploadResult.total_registros}</h3>
            </div>

            <div className="stat-card success">
              <span>Válidos</span>
              <h3>{uploadResult.total_validos}</h3>
            </div>

            <div className="stat-card error">
              <span>Inválidos</span>
              <h3>{uploadResult.total_invalidos}</h3>
            </div>

            <div className="stat-card">
              <span>Sucesso</span>
              <h3>{percentualSucesso}%</h3>
            </div>

          </div>

          {uploadResult.registros_invalidos?.length > 0 && (
            <>
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
                  {uploadResult.registros_invalidos.map(
                    (item) => (
                      <tr key={item.linha}>
                        <td>{item.linha}</td>

                        <td>
                          {item.produto || "-"}
                        </td>

                        <td>
                          {item.erros.join(", ")}
                        </td>
                      </tr>
                    )
                  )}
                </tbody>
              </table>
            </>
          )}

          {uploadResult.registros_processados?.length > 0 && (
            <>
              <h3>Produtos cruzados automaticamente</h3>

              <table>
                <thead>
                  <tr>
                    <th>Produto da planilha</th>
                    <th>Produto encontrado</th>
                    <th>Status</th>
                    <th>Confiança</th>
                  </tr>
                </thead>

                <tbody>
                  {uploadResult.registros_processados.map(
                    (item, index) => (
                      <tr key={index}>
                        <td>{item.produto}</td>

                        <td>
                          {item.produto_cadastrado || "-"}
                        </td>

                        <td>
                          <span
                            className={`status ${item.status_cruzamento}`}
                          >
                            {item.status_cruzamento}
                          </span>
                        </td>

                        <td>
                          {Math.round(
                            item.confianca_cruzamento * 100
                          )}%
                        </td>
                      </tr>
                    )
                  )}
                </tbody>
              </table>
            </>
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
              <th>Data/Hora</th>
            </tr>
          </thead>

          <tbody>
            {imports.map((item) => (
              <tr key={item.id}>
                <td>{item.id}</td>

                <td>{item.nome_arquivo}</td>

                <td>{item.usuario_nome}</td>

                <td>
                  <span
                    className={`status ${item.status}`}
                  >
                    {item.status}
                  </span>
                </td>

                <td>{item.observacao}</td>
                <td>{item.created_at}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </Layout>
  );
}