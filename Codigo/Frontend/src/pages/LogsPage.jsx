import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";
import api from "../api/client";
import { formatDateTime, errorMessage } from "../utils/format";



const TIPOS = [
  { value: "", label: "Todos os eventos" },
  { value: "importacao_planilha", label: "Importação de planilha" },
  { value: "validacao_planilha", label: "Validação de planilha" },
  { value: "cruzamento_produtos", label: "Cruzamento de produtos" },
  { value: "geracao_relatorio", label: "Geração de relatório" },
  { value: "envio_relatorio_agendado", label: "Envio de relatório agendado" },
  { value: "alteracao_permissoes", label: "Alteração de permissões" },
];

const TIPO_LABEL = TIPOS.reduce((acc, t) => {
  if (t.value) acc[t.value] = t.label;
  return acc;
}, {});

export default function LogsPage() {
  const [logs, setLogs] = useState([]);
  const [tipo, setTipo] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async (tipoOperacao) => {
    setLoading(true);
    setError("");
    try {
      const params = {};
      if (tipoOperacao) params.tipo_operacao = tipoOperacao;
      const { data } = await api.get("/logs", { params });
      setLogs(data);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load(tipo);
  }, [tipo]);

  return (
    <Layout
      title="Logs de Auditoria"
      crumb="Administração"
      intro="Registro cronológico das operações críticas do sistema, garantindo rastreabilidade e segurança."
      actions={
        <button className="btn btn-ghost btn-sm" onClick={() => load(tipo)}>Atualizar</button>
      }
    >
      {error && <div className="note error">{error}</div>}

      <div className="panel">
        <div className="panel-head">
          <h2>Eventos Registrados</h2>
          <div className="field" style={{ marginBottom: 0, minWidth: 220 }}>
            <select value={tipo} onChange={(e) => setTipo(e.target.value)}>
              {TIPOS.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
            </select>
          </div>
        </div>

        {loading ? (
          <div><span className="spinner" /> Carregando logs...</div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Data / Hora</th>
                  <th>Evento</th>
                  <th>Usuário</th>
                  <th>Resumo</th>
                </tr>
              </thead>
              <tbody>
                {logs.length === 0 ? (
                  <tr><td className="table-empty" colSpan={4}>Nenhum evento registrado.</td></tr>
                ) : (
                  logs.map((log) => (
                    <tr key={log.id}>
                      <td style={{ whiteSpace: "nowrap" }}>{formatDateTime(log.data_hora)}</td>
                      <td><span className="badge info">{TIPO_LABEL[log.tipo_operacao] || log.tipo_operacao}</span></td>
                      <td className="strong">{log.usuario}</td>
                      <td>{log.resumo}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Layout>
  );
}
