import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { BrandMark } from "../components/Icon";
import { errorMessage } from "../utils/format";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate("/");
    } catch (err) {
      setError(errorMessage(err, "Não foi possível entrar. Verifique suas credenciais."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-screen">
      <aside className="login-aside">
        <div className="login-brand">
          <BrandMark size={42} />
          <span className="name">Dash<b>Vendas</b></span>
        </div>

        <div className="login-pitch">
          <div className="eyebrow">Plataforma de Análise Comercial</div>
          <h1>
            Transforme dados de vendas em <em>decisões</em> com inteligência.
          </h1>
          <p>
            Importação estruturada de planilhas, cálculo automatizado de KPIs,
            acompanhamento de metas, alertas de desempenho e um assistente de IA
            para interpretar seus números.
          </p>
        </div>

        <div className="login-metrics">
          <div className="m">
            <div className="v">KPIs</div>
            <div className="l">Cálculo automatizado</div>
          </div>
          <div className="m">
            <div className="v">IA</div>
            <div className="l">Análise interpretativa</div>
          </div>
          <div className="m">
            <div className="v">5</div>
            <div className="l">Perfis de acesso</div>
          </div>
        </div>
      </aside>

      <div className="login-main">
        <div className="login-card">
          <h2>Acessar o sistema</h2>
          <p className="sub">Entre com suas credenciais corporativas.</p>

          {error && <div className="note error">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="field">
              <label htmlFor="email">E-mail</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="seu.email@dashvendas.com"
                autoComplete="username"
                required
              />
            </div>

            <div className="field">
              <label htmlFor="password">Senha</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••"
                autoComplete="current-password"
                required
              />
            </div>

            <button type="submit" className="btn btn-block" disabled={loading}>
              {loading ? <span className="spinner" /> : "Entrar"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
