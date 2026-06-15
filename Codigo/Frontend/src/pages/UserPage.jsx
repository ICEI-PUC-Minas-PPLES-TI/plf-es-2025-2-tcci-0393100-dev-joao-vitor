import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";
import api from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { errorMessage } from "../utils/format";

/* Gestão de usuários (UC14 / CO15).
   Permite ao administrador criar, editar perfil/status e remover
   usuários. Cada alteração é registrada em log de auditoria no backend. */

const ROLES = [
  { value: "administrador", label: "Administrador" },
  { value: "gestor", label: "Gestor" },
  { value: "analista", label: "Analista" },
  { value: "vendedor", label: "Vendedor" },
  { value: "executivo", label: "Executivo" },
];

const EMPTY_FORM = { nome: "", email: "", senha: "", tipo_usuario: "vendedor" };

export default function UserPage() {
  const { user } = useAuth();
  const [usuarios, setUsuarios] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const { data } = await api.get("/usuarios");
      setUsuarios(data);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      await api.post("/usuarios", form);
      setForm(EMPTY_FORM);
      setSuccess("Usuário criado com sucesso.");
      load();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  const alterarPerfil = async (u, tipo_usuario) => {
    try {
      await api.put(`/usuarios/${u.id}`, { tipo_usuario });
      load();
    } catch (err) {
      setError(errorMessage(err));
    }
  };

  const alternarStatus = async (u) => {
    try {
      await api.put(`/usuarios/${u.id}`, { ativo: !u.ativo });
      load();
    } catch (err) {
      setError(errorMessage(err));
    }
  };

  const remover = async (id) => {
    if (!window.confirm("Remover este usuário?")) return;
    try {
      await api.delete(`/usuarios/${id}`);
      load();
    } catch (err) {
      setError(errorMessage(err));
    }
  };

  return (
    <Layout
      title="Gestão de Usuários"
      crumb="Administração"
      intro="Cadastre usuários, ajuste perfis de acesso e ative ou desative contas. Todas as alterações ficam registradas na auditoria."
    >
      {error && <div className="note error">{error}</div>}
      {success && <div className="note ok">{success}</div>}

      <div className="panel">
        <div className="panel-head"><h2>Novo Usuário</h2></div>
        <form onSubmit={handleSubmit}>
          <div className="toolbar">
            <div className="field">
              <label>Nome</label>
              <input type="text" value={form.nome} required
                onChange={(e) => setForm({ ...form, nome: e.target.value })} />
            </div>
            <div className="field">
              <label>E-mail</label>
              <input type="email" value={form.email} required
                onChange={(e) => setForm({ ...form, email: e.target.value })} />
            </div>
            <div className="field">
              <label>Senha</label>
              <input type="password" value={form.senha} required
                onChange={(e) => setForm({ ...form, senha: e.target.value })} />
            </div>
            <div className="field">
              <label>Perfil</label>
              <select value={form.tipo_usuario}
                onChange={(e) => setForm({ ...form, tipo_usuario: e.target.value })}>
                {ROLES.map((r) => <option key={r.value} value={r.value}>{r.label}</option>)}
              </select>
            </div>
            <button type="submit" className="btn btn-sm" disabled={busy}>
              {busy ? <span className="spinner" /> : "Criar usuário"}
            </button>
          </div>
        </form>
      </div>

      <div className="panel">
        <div className="panel-head">
          <h2>Usuários do Sistema</h2>
          <span className="hint">{usuarios.length} usuário(s)</span>
        </div>
        {loading ? (
          <div><span className="spinner" /> Carregando usuários...</div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Nome</th>
                  <th>E-mail</th>
                  <th>Perfil</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {usuarios.map((u) => (
                  <tr key={u.id}>
                    <td className="strong">{u.nome}{u.id === user?.id && <span className="badge muted" style={{ marginLeft: 8 }}>você</span>}</td>
                    <td>{u.email}</td>
                    <td>
                      <select
                        value={u.role}
                        disabled={u.id === user?.id}
                        onChange={(e) => alterarPerfil(u, e.target.value)}
                        style={{ padding: "6px 10px", fontSize: "0.82rem" }}
                      >
                        {ROLES.map((r) => <option key={r.value} value={r.value}>{r.label}</option>)}
                      </select>
                    </td>
                    <td><span className={`badge ${u.ativo ? "ativo" : "inativo"}`}>{u.ativo ? "Ativo" : "Inativo"}</span></td>
                    <td>
                      <div className="row-actions">
                        <button
                          className="btn btn-ghost btn-sm"
                          disabled={u.id === user?.id}
                          onClick={() => alternarStatus(u)}
                        >
                          {u.ativo ? "Desativar" : "Ativar"}
                        </button>
                        <button
                          className="btn btn-danger btn-sm"
                          disabled={u.id === user?.id}
                          onClick={() => remover(u.id)}
                        >
                          Remover
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Layout>
  );
}
