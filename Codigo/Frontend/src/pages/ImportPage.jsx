import React, { useEffect, useRef, useState } from "react";
import Layout from "../components/Layout";
import api from "../api/client";
import {
  formatNumber,
  formatPercent,
  statusLabel,
  formatDateTime,
  errorMessage,
} from "../utils/format";

/* Importação de planilhas em 3 etapas (UC08, UC09, UC10).
   Etapa 1 — Upload (CO09): envia o arquivo .xlsx.
   Etapa 2 — Validação (CO10): valida estrutura e campos.
   Etapa 3 — Cruzamento (CO11): casa produtos e consolida as vendas.
   Acompanha o protótipo (Escolher arquivo → Importar → Validação). */

const STEPS = [
  { key: "upload", t: "1. Importar", d: "Enviar planilha .xlsx" },
  { key: "validacao", t: "2. Validar", d: "Conferir estrutura e dados" },
  { key: "cruzamento", t: "3. Cruzar", d: "Casar produtos e consolidar" },
];

export default function ImportPage() {
  const fileInputRef = useRef(null);

  const [file, setFile] = useState(null);
  const [importacao, setImportacao] = useState(null);
  const [stepDone, setStepDone] = useState({ upload: false, validacao: false, cruzamento: false });
  const [validacao, setValidacao] = useState(null);
  const [cruzamento, setCruzamento] = useState(null);
  const [itens, setItens] = useState([]);
  const [historico, setHistorico] = useState([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const loadHistorico = async () => {
    try {
      const { data } = await api.get("/imports");
      setHistorico(data);
    } catch (err) {
      // histórico é complementar; não bloqueia o fluxo
    }
  };

  useEffect(() => {
    loadHistorico();
  }, []);

  const currentStep = !stepDone.upload
    ? "upload"
    : !stepDone.validacao
    ? "validacao"
    : "cruzamento";

  const resetFluxo = () => {
    setFile(null);
    setImportacao(null);
    setStepDone({ upload: false, validacao: false, cruzamento: false });
    setValidacao(null);
    setCruzamento(null);
    setItens([]);
    setError("");
    setSuccess("");
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleFileChange = (event) => {
    const selected = event.target.files?.[0] || null;
    setFile(selected);
    setError("");
  };

  const loadItens = async (importacaoId) => {
    try {
      const { data } = await api.get(`/imports/${importacaoId}/itens`);
      setItens(data);
    } catch (err) {
      // itens são complementares
    }
  };

  /* Etapa 1 — Upload */
  const handleUpload = async (event) => {
    event.preventDefault();
    if (!file) {
      setError("Selecione um arquivo .xlsx para importar.");
      return;
    }
    setLoading(true);
    setError("");
    setSuccess("");
    try {
      const formData = new FormData();
      formData.append("arquivo", file);
      const { data } = await api.post("/imports/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setImportacao(data.importacao);
      setStepDone({ upload: true, validacao: false, cruzamento: false });
      setSuccess(`${data.message} (${data.total_registros} registros)`);
      loadHistorico();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  /* Etapa 2 — Validação */
  const handleValidar = async () => {
    if (!importacao) return;
    setLoading(true);
    setError("");
    setSuccess("");
    try {
      const { data } = await api.post(`/imports/${importacao.id}/validar`);
      setValidacao(data);
      setImportacao(data.importacao);
      setStepDone((prev) => ({ ...prev, validacao: true }));
      setSuccess(data.resumo);
      loadItens(importacao.id);
      loadHistorico();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  /* Etapa 3 — Cruzamento */
  const handleCruzar = async () => {
    if (!importacao) return;
    setLoading(true);
    setError("");
    setSuccess("");
    try {
      const { data } = await api.post(`/imports/${importacao.id}/cruzar`);
      setCruzamento(data);
      setImportacao(data.importacao);
      setStepDone((prev) => ({ ...prev, cruzamento: true }));
      setSuccess(data.resumo);
      loadItens(importacao.id);
      loadHistorico();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout
      title="Importação de Planilhas"
      crumb="Operações"
      intro="Importe os dados de vendas em três etapas: envio do arquivo, validação da estrutura e cruzamento de produtos com o catálogo interno."
      actions={
        (importacao || file) && (
          <button className="btn btn-ghost btn-sm" onClick={resetFluxo}>
            Nova importação
          </button>
        )
      }
    >
      {error && <div className="note error">{error}</div>}
      {success && <div className="note ok">{success}</div>}

      <div className="stepper">
        {STEPS.map((step) => {
          const cls = stepDone[step.key]
            ? "done"
            : currentStep === step.key
            ? "current"
            : "";
          return (
            <div className={`step ${cls}`} key={step.key}>
              <div className="num">{stepDone[step.key] ? "✓" : STEPS.indexOf(step) + 1}</div>
              <div className="txt">
                <div className="t">{step.t}</div>
                <div className="d">{step.d}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Etapa 1 — Upload */}
      <div className="panel">
        <div className="panel-head">
          <h2>Etapa 1 · Enviar planilha</h2>
          {importacao && <span className={`badge ${importacao.status}`}>{statusLabel(importacao.status)}</span>}
        </div>

        {!stepDone.upload ? (
          <form onSubmit={handleUpload}>
            <label className="file-drop" htmlFor="file-input">
              <div className="ico">⬆</div>
              <div className="main">{file ? "Arquivo selecionado" : "Escolher arquivo .xlsx"}</div>
              <div className="sub">
                Colunas obrigatórias: data_venda, vendedor, regiao, produto, categoria,
                quantidade, valor_unitario, valor_total
              </div>
              {file && <div className="file-chosen">{file.name}</div>}
              <input
                id="file-input"
                ref={fileInputRef}
                type="file"
                accept=".xlsx,.xls"
                onChange={handleFileChange}
              />
            </label>
            <div style={{ marginTop: 16 }}>
              <button type="submit" className="btn" disabled={loading || !file}>
                {loading ? <span className="spinner" /> : "Importar planilha"}
              </button>
            </div>
          </form>
        ) : (
          <p style={{ color: "var(--text-2)" }}>
            Planilha <b>{importacao?.nome_arquivo}</b> importada. Prossiga para a validação.
          </p>
        )}
      </div>

      {/* Etapa 2 — Validação */}
      {stepDone.upload && (
        <div className="panel">
          <div className="panel-head">
            <h2>Etapa 2 · Validação</h2>
            {!stepDone.validacao && (
              <button className="btn btn-sm" onClick={handleValidar} disabled={loading}>
                {loading ? <span className="spinner" /> : "Validar planilha"}
              </button>
            )}
          </div>

          {validacao && (
            <>
              <div className="stat-mini">
                <div className="s">
                  <div className="v">{formatNumber(validacao.total_registros)}</div>
                  <div className="l">Registros</div>
                </div>
                <div className="s ok">
                  <div className="v">{formatNumber(validacao.total_validos)}</div>
                  <div className="l">Válidos</div>
                </div>
                <div className="s danger">
                  <div className="v">{formatNumber(validacao.total_invalidos)}</div>
                  <div className="l">Inválidos</div>
                </div>
                <div className="s">
                  <div className="v">
                    {formatPercent(
                      validacao.total_registros
                        ? (validacao.total_validos / validacao.total_registros) * 100
                        : 0,
                      0
                    )}
                  </div>
                  <div className="l">Aproveitamento</div>
                </div>
              </div>

              {validacao.registros_invalidos?.length > 0 && (
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Linha</th>
                        <th>Produto</th>
                        <th>Inconsistências</th>
                      </tr>
                    </thead>
                    <tbody>
                      {validacao.registros_invalidos.map((r, idx) => (
                        <tr key={idx}>
                          <td className="num">{r.linha}</td>
                          <td className="strong">{r.produto || "—"}</td>
                          <td>
                            {(r.erros || []).map((e, i) => (
                              <span key={i} className="badge danger" style={{ marginRight: 4 }}>{e}</span>
                            ))}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* Etapa 3 — Cruzamento */}
      {stepDone.validacao && (
        <div className="panel">
          <div className="panel-head">
            <h2>Etapa 3 · Cruzamento de produtos</h2>
            {!stepDone.cruzamento && (
              <button className="btn btn-sm" onClick={handleCruzar} disabled={loading}>
                {loading ? <span className="spinner" /> : "Executar cruzamento"}
              </button>
            )}
          </div>

          {cruzamento && (
            <>
              <div className="stat-mini">
                <div className="s">
                  <div className="v">{formatNumber(cruzamento.total_itens)}</div>
                  <div className="l">Itens válidos</div>
                </div>
                <div className="s ok">
                  <div className="v">{formatNumber(cruzamento.encontrados)}</div>
                  <div className="l">Encontrados</div>
                </div>
                <div className="s danger">
                  <div className="v">{formatNumber(cruzamento.nao_encontrados)}</div>
                  <div className="l">Não encontrados</div>
                </div>
                <div className="s">
                  <div className="v">{formatPercent(cruzamento.criterio_similaridade_minima * 100, 0)}</div>
                  <div className="l">Similaridade mín.</div>
                </div>
              </div>

              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Linha</th>
                      <th>Item da Planilha</th>
                      <th>Produto Correspondente</th>
                      <th className="num">Confiança</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(cruzamento.registros_processados || []).map((r, idx) => (
                      <tr key={idx}>
                        <td className="num">{r.linha}</td>
                        <td className="strong">{r.produto}</td>
                        <td>{r.produto_cadastrado || <span style={{ color: "var(--text-3)" }}>—</span>}</td>
                        <td className="num">{formatPercent((r.confianca_cruzamento || 0) * 100, 0)}</td>
                        <td><span className={`badge ${r.status_cruzamento}`}>{statusLabel(r.status_cruzamento)}</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      )}

      {/* Histórico de importações */}
      <div className="panel">
        <div className="panel-head">
          <h2>Histórico de Importações</h2>
          <button className="btn btn-ghost btn-sm" onClick={loadHistorico}>Atualizar</button>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Arquivo</th>
                <th>Responsável</th>
                <th>Status</th>
                <th>Data</th>
              </tr>
            </thead>
            <tbody>
              {historico.length === 0 ? (
                <tr><td className="table-empty" colSpan={4}>Nenhuma importação registrada.</td></tr>
              ) : (
                historico.map((h) => (
                  <tr key={h.id}>
                    <td className="strong">{h.nome_arquivo}</td>
                    <td>{h.usuario_nome}</td>
                    <td><span className={`badge ${h.status}`}>{statusLabel(h.status)}</span></td>
                    <td>{formatDateTime(h.created_at)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </Layout>
  );
}
