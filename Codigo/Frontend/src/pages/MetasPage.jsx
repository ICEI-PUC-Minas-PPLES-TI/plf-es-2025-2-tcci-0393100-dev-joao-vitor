import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";
import api from "../api/client";
import { useAuth } from "../auth/AuthContext";
import {
  formatCurrency,
  formatPercent,
  statusLabel,
  errorMessage,
} from "../utils/format";



const EMPTY_FORM = {
  periodo_inicio: "",
  periodo_fim: "",
  regiao: "",
  categoria: "",
  valor_meta: "",
  descricao: "",
};

export default function MetasPage() {
  const { user } = useAuth();
  const podeEditar = ["gestor", "administrador"].includes(user?.role);

  const [metas, setMetas] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const { data } = await api.get("/metas");
      setMetas(data);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError("");
    setSuccess("");
    try {
      await api.post("/metas", {
        periodo_inicio: form.periodo_inicio,
        periodo_fim: form.periodo_fim,
        regiao: form.regiao || null,
        categoria: form.categoria || null,
        valor_meta: Number(form.valor_meta),
        descricao: form.descricao || null,
      });
      setForm(EMPTY_FORM);
      setSuccess("Meta cadastrada com sucesso.");
      load();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Remover esta meta?")) return;
    try {
      await api.delete(`/metas/${id}`);
      load();
    } catch (err) {
      setError(errorMessage(err));
    }
  };

  return (
    <Layout
      title="Metas Comerciais"
      crumb="Análise"
      intro="Defina metas por período, região ou categoria e acompanhe o percentual de atingimento em relação às vendas realizadas."
    >
      {error && <div className="note error">{error}</div>}
      {success && <div className="note ok">{success}</div>}

      {podeEditar && (
        <div className="panel">
          <div className="panel-head"><h2>Nova Meta</h2></div>
          <form onSubmit={handleSubmit}>
            <div className="toolbar">
              <div className="field">
                <label>Período inicial</label>
                <input type="date" name="periodo_inicio" value={form.periodo_inicio} onChange={handleChange} required />
              </div>
              <div className="field">
                <label>Período final</label>
                <input type="date" name="periodo_fim" value={form.periodo_fim} onChange={handleChange} required />
              </div>
              <div className="field">
                <label>Região (opcional)</label>
                <input type="text" name="regiao" value={form.regiao} onChange={handleChange} placeholder="Todas" />
              </div>
              <div className="field">
                <label>Categoria (opcional)</label>
                <input type="text" name="categoria" value={form.categoria} onChange={handleChange} placeholder="Todas" />
              </div>
              <div className="field">
                <label>Valor da meta (R$)</label>
                <input type="number" step="0.01" min="0" name="valor_meta" value={form.valor_meta} onChange={handleChange} placeholder="50000" required />
              </div>
              <div className="field" style={{ minWidth: 200 }}>
                <label>Descrição (opcional)</label>
                <input type="text" name="descricao" value={form.descricao} onChange={handleChange} placeholder="Meta trimestral Sudeste" />
              </div>
              <button type="submit" className="btn btn-sm" disabled={saving}>
                {saving ? <span className="spinner" /> : "Cadastrar meta"}
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="panel">
        <div className="panel-head">
          <h2>Acompanhamento de Metas</h2>
          <span className="hint">{metas.length} meta(s) cadastrada(s)</span>
        </div>

        {loading ? (
          <div><span className="spinner" /> Carregando metas...</div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Período</th>
                  <th>Segmento</th>
                  <th className="num">Meta</th>
                  <th className="num">Realizado</th>
                  <th>Atingimento</th>
                  <th>Status</th>
                  {podeEditar && <th></th>}
                </tr>
              </thead>
              <tbody>
                {metas.length === 0 ? (
                  <tr><td className="table-empty" colSpan={podeEditar ? 7 : 6}>Nenhuma meta cadastrada ainda.</td></tr>
                ) : (
                  metas.map((meta) => (
                    <tr key={meta.id}>
                      <td>{meta.periodo_inicio} <span style={{ color: "var(--text-3)" }}>a</span> {meta.periodo_fim}</td>
                      <td>
                        {meta.regiao || meta.categoria
                          ? [meta.regiao, meta.categoria].filter(Boolean).join(" · ")
                          : <span style={{ color: "var(--text-3)" }}>Geral</span>}
                        {meta.descricao && <div style={{ fontSize: "0.76rem", color: "var(--text-3)" }}>{meta.descricao}</div>}
                      </td>
                      <td className="num">{formatCurrency(meta.valor_meta)}</td>
                      <td className="num">{formatCurrency(meta.total_realizado)}</td>
                      <td style={{ minWidth: 140 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                          <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.82rem" }}>
                            {formatPercent(meta.percentual_atingimento)}
                          </span>
                        </div>
                        <div className="meta-bar">
                          <span
                            className={meta.status}
                            style={{ width: `${Math.min(meta.percentual_atingimento, 100)}%` }}
                          />
                        </div>
                      </td>
                      <td><span className={`badge ${meta.status}`}>{statusLabel(meta.status)}</span></td>
                      {podeEditar && (
                        <td>
                          <button className="btn btn-danger btn-sm" onClick={() => handleDelete(meta.id)}>
                            Remover
                          </button>
                        </td>
                      )}
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
