import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";
import api from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { formatDateTime, statusLabel, errorMessage } from "../utils/format";



const EMPTY_REPORT = { periodo_inicio: "", periodo_fim: "", regiao: "", categoria: "" };
const EMPTY_SCHEDULE = { periodicidade: "mensal", destinatarios: "", filtros: "" };

export default function RelatoriosPage() {
  const { user } = useAuth();
  const podeGerar = ["gestor", "administrador"].includes(user?.role);

  const [reportForm, setReportForm] = useState(EMPTY_REPORT);
  const [scheduleForm, setScheduleForm] = useState(EMPTY_SCHEDULE);
  const [relatorios, setRelatorios] = useState([]);
  const [agendamentos, setAgendamentos] = useState([]);

  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const requests = [api.get("/relatorios")];
      if (podeGerar) requests.push(api.get("/agendamentos"));
      const res = await Promise.all(requests);
      setRelatorios(res[0].data);
      if (podeGerar && res[1]) setAgendamentos(res[1].data);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const gerarRelatorio = async (event) => {
    event.preventDefault();
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      const params = {};
      Object.entries(reportForm).forEach(([k, v]) => {
        if (v) params[k] = v;
      });
      await api.post("/relatorios/gerar", null, { params });
      setSuccess("Relatório gerado com sucesso.");
      setReportForm(EMPTY_REPORT);
      load();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  const baixarRelatorio = async (id) => {
    try {
      const response = await api.get(`/relatorios/${id}/download`, { responseType: "blob" });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `relatorio_${id}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(errorMessage(err));
    }
  };

  const criarAgendamento = async (event) => {
    event.preventDefault();
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      await api.post("/agendamentos", {
        periodicidade: scheduleForm.periodicidade,
        destinatarios: scheduleForm.destinatarios,
        filtros: scheduleForm.filtros || null,
      });
      setScheduleForm(EMPTY_SCHEDULE);
      setSuccess("Agendamento criado.");
      load();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  const alternarAgendamento = async (ag) => {
    try {
      await api.patch(`/agendamentos/${ag.id}`, { ativo: !ag.ativo });
      load();
    } catch (err) {
      setError(errorMessage(err));
    }
  };

  const removerAgendamento = async (id) => {
    if (!window.confirm("Remover este agendamento?")) return;
    try {
      await api.delete(`/agendamentos/${id}`);
      load();
    } catch (err) {
      setError(errorMessage(err));
    }
  };

  const executarEnvios = async () => {
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      const { data } = await api.post("/agendamentos/executar");
      setSuccess(data.message);
      load();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Layout
      title="Relatórios"
      crumb="Operações"
      intro="Gere relatórios consolidados de vendas e metas, faça o download e configure envios periódicos automáticos."
    >
      {error && <div className="note error">{error}</div>}
      {success && <div className="note ok">{success}</div>}

      {podeGerar && (
        <div className="panel">
          <div className="panel-head"><h2>Gerar Relatório</h2></div>
          <form onSubmit={gerarRelatorio}>
            <div className="toolbar">
              <div className="field">
                <label>Período inicial</label>
                <input type="date" value={reportForm.periodo_inicio}
                  onChange={(e) => setReportForm({ ...reportForm, periodo_inicio: e.target.value })} />
              </div>
              <div className="field">
                <label>Período final</label>
                <input type="date" value={reportForm.periodo_fim}
                  onChange={(e) => setReportForm({ ...reportForm, periodo_fim: e.target.value })} />
              </div>
              <div className="field">
                <label>Região (opcional)</label>
                <input type="text" value={reportForm.regiao} placeholder="Todas"
                  onChange={(e) => setReportForm({ ...reportForm, regiao: e.target.value })} />
              </div>
              <div className="field">
                <label>Categoria (opcional)</label>
                <input type="text" value={reportForm.categoria} placeholder="Todas"
                  onChange={(e) => setReportForm({ ...reportForm, categoria: e.target.value })} />
              </div>
              <button type="submit" className="btn btn-sm" disabled={busy}>
                {busy ? <span className="spinner" /> : "Gerar relatório"}
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="panel">
        <div className="panel-head">
          <h2>Histórico de Relatórios</h2>
          <button className="btn btn-ghost btn-sm" onClick={load}>Atualizar</button>
        </div>
        {loading ? (
          <div><span className="spinner" /> Carregando...</div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Tipo</th>
                  <th>Período</th>
                  <th>Origem</th>
                  <th>Gerado em</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {relatorios.length === 0 ? (
                  <tr><td className="table-empty" colSpan={6}>Nenhum relatório gerado ainda.</td></tr>
                ) : (
                  relatorios.map((r) => (
                    <tr key={r.id}>
                      <td className="num">{r.id}</td>
                      <td className="strong">{r.tipo}</td>
                      <td>{r.periodo || "Completo"}</td>
                      <td>{r.id_agendamento ? <span className="badge info">Agendado</span> : <span className="badge muted">Sob demanda</span>}</td>
                      <td>{formatDateTime(r.data_geracao)}</td>
                      <td>
                        <button className="btn btn-ghost btn-sm" onClick={() => baixarRelatorio(r.id)}>
                          Baixar CSV
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {podeGerar && (
        <>
          <div className="panel">
            <div className="panel-head"><h2>Novo Agendamento</h2></div>
            <form onSubmit={criarAgendamento}>
              <div className="toolbar">
                <div className="field">
                  <label>Periodicidade</label>
                  <select value={scheduleForm.periodicidade}
                    onChange={(e) => setScheduleForm({ ...scheduleForm, periodicidade: e.target.value })}>
                    <option value="diario">Diário</option>
                    <option value="semanal">Semanal</option>
                    <option value="mensal">Mensal</option>
                  </select>
                </div>
                <div className="field" style={{ minWidth: 240 }}>
                  <label>Destinatários (e-mails)</label>
                  <input type="text" value={scheduleForm.destinatarios} required
                    placeholder="gestor@empresa.com, diretoria@empresa.com"
                    onChange={(e) => setScheduleForm({ ...scheduleForm, destinatarios: e.target.value })} />
                </div>
                <div className="field" style={{ minWidth: 180 }}>
                  <label>Filtros (opcional)</label>
                  <input type="text" value={scheduleForm.filtros} placeholder="Ex.: Sudeste"
                    onChange={(e) => setScheduleForm({ ...scheduleForm, filtros: e.target.value })} />
                </div>
                <button type="submit" className="btn btn-sm" disabled={busy}>Agendar</button>
              </div>
            </form>
          </div>

          <div className="panel">
            <div className="panel-head">
              <h2>Agendamentos Ativos</h2>
              <button className="btn btn-sm" onClick={executarEnvios} disabled={busy}>
                {busy ? <span className="spinner" /> : "Executar envios agora"}
              </button>
            </div>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Periodicidade</th>
                    <th>Destinatários</th>
                    <th>Filtros</th>
                    <th>Último envio</th>
                    <th>Status</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {agendamentos.length === 0 ? (
                    <tr><td className="table-empty" colSpan={6}>Nenhum agendamento configurado.</td></tr>
                  ) : (
                    agendamentos.map((ag) => (
                      <tr key={ag.id}>
                        <td className="strong" style={{ textTransform: "capitalize" }}>{ag.periodicidade}</td>
                        <td>{ag.destinatarios}</td>
                        <td>{ag.filtros || "—"}</td>
                        <td>{ag.ultimo_envio ? formatDateTime(ag.ultimo_envio) : "Nunca"}</td>
                        <td><span className={`badge ${ag.ativo ? "ativo" : "inativo"}`}>{ag.ativo ? "Ativo" : "Inativo"}</span></td>
                        <td>
                          <div className="row-actions">
                            <button className="btn btn-ghost btn-sm" onClick={() => alternarAgendamento(ag)}>
                              {ag.ativo ? "Desativar" : "Ativar"}
                            </button>
                            <button className="btn btn-danger btn-sm" onClick={() => removerAgendamento(ag.id)}>
                              Remover
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </Layout>
  );
}
