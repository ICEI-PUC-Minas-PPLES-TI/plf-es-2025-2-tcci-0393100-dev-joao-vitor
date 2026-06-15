import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Layout from "../components/Layout";
import BarChart from "../components/BarChart";
import api from "../api/client";
import { useAuth } from "../auth/AuthContext";
import {
  formatCurrency,
  formatNumber,
  formatPercent,
  errorMessage,
} from "../utils/format";

/* Dashboard — visão geral (CT01).
   Exibe os KPIs consolidados, o gráfico de vendas por região e os
   alertas mais recentes, conforme o protótipo da documentação. */

export default function DashboardPage() {
  const { user } = useAuth();
  const [summary, setSummary] = useState(null);
  const [alertas, setAlertas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const canSeeAlertas = ["gestor", "administrador", "executivo"].includes(user?.role);

  useEffect(() => {
    let active = true;

    async function load() {
      setLoading(true);
      setError("");
      try {
        const requests = [api.get("/dashboard/summary")];
        if (canSeeAlertas) {
          requests.push(api.get("/alertas", { params: { apenas_nao_lidos: false } }));
        }
        const responses = await Promise.all(requests);
        if (!active) return;
        setSummary(responses[0].data);
        if (canSeeAlertas && responses[1]) {
          setAlertas(responses[1].data.slice(0, 5));
        }
      } catch (err) {
        if (active) setError(errorMessage(err));
      } finally {
        if (active) setLoading(false);
      }
    }

    load();
    return () => {
      active = false;
    };
  }, [canSeeAlertas]);

  const resumo = summary?.resumo;
  const porRegiao = (summary?.por_regiao || []).map((r) => ({
    label: r.regiao,
    value: r.total_vendas,
  }));

  return (
    <Layout
      title="Dashboard"
      crumb="Visão Geral"
      intro={`Bem-vindo, ${user?.nome?.split(" ")[0] || "usuário"}. Acompanhe o desempenho comercial consolidado.`}
    >
      {error && <div className="note error">{error}</div>}

      {loading ? (
        <div className="panel">
          <span className="spinner" /> Carregando indicadores...
        </div>
      ) : (
        <>
          <div className="kpi-grid">
            <div className="kpi">
              <div className="label">Total de Vendas</div>
              <div className="value">
                <span className="cur">R$</span>
                {formatNumber(resumo?.total_vendas, 2)}
              </div>
              <div className="foot">Faturamento consolidado</div>
            </div>

            <div className="kpi teal">
              <div className="label">Pedidos</div>
              <div className="value">{formatNumber(resumo?.total_pedidos)}</div>
              <div className="foot">Total de vendas registradas</div>
            </div>

            <div className="kpi info">
              <div className="label">Ticket Médio</div>
              <div className="value">
                <span className="cur">R$</span>
                {formatNumber(resumo?.ticket_medio, 2)}
              </div>
              <div className="foot">Valor médio por pedido</div>
            </div>

            <div className="kpi ok">
              <div className="label">Atingimento de Metas</div>
              <div className="value">{formatPercent(resumo?.meta_percentual)}</div>
              <div className="foot">Média das metas cadastradas</div>
            </div>
          </div>

          <div className="grid-2">
            <div className="panel">
              <div className="panel-head">
                <h2>Vendas por Região</h2>
                <Link className="hint" to="/kpis">Ver indicadores →</Link>
              </div>
              <BarChart
                data={porRegiao}
                valueFormatter={formatCurrency}
                emptyText="Nenhuma venda consolidada ainda. Importe uma planilha para começar."
              />
            </div>

            <div className="panel">
              <div className="panel-head">
                <h2>Alertas Recentes</h2>
                {canSeeAlertas && <Link className="hint" to="/alertas">Ver todos →</Link>}
              </div>

              {!canSeeAlertas ? (
                <p className="chat-empty" style={{ margin: "24px 0" }}>
                  Alertas disponíveis para perfis de gestão.
                </p>
              ) : alertas.length === 0 ? (
                <p className="chat-empty" style={{ margin: "24px 0" }}>
                  Nenhum alerta no momento. Tudo sob controle.
                </p>
              ) : (
                <div className="bars" style={{ gap: "12px" }}>
                  {alertas.map((a) => (
                    <div key={a.id} className="note" style={{ marginBottom: 0 }}>
                      <span className={`pill-level ${a.nivel_criticidade}`} style={{ flexShrink: 0 }}>
                        {a.nivel_criticidade}
                      </span>
                      <span style={{ fontSize: "0.85rem", color: "var(--text-2)" }}>
                        {a.mensagem}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </Layout>
  );
}
