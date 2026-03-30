import React, { useEffect, useState } from "react";
import Layout from "../components/layout";
import api from "../api/client";

export default function DashboardPage() {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadData() {
      try {
        const res = await api.get("/dashboard/summary");
        setSummary(res.data);
      } catch (err) {
        setError("Não foi possível carregar o dashboard.");
      }
    }

    loadData();
  }, []);

  return (
    <Layout>
      <h1>Dashboard inicial</h1>
      <p>Base do sistema pronta para a próxima fase.</p>

      {error && <p className="error">{error}</p>}

      <div className="grid">
        <div className="card stat">
          <h3>Total de vendas</h3>
          <p>R$ {summary?.resumo?.total_vendas ?? 0}</p>
        </div>

        <div className="card stat">
          <h3>Total de pedidos</h3>
          <p>{summary?.resumo?.total_pedidos ?? 0}</p>
        </div>

        <div className="card stat">
          <h3>Ticket médio</h3>
          <p>R$ {summary?.resumo?.ticket_medio ?? 0}</p>
        </div>

        <div className="card stat">
          <h3>% da meta</h3>
          <p>{summary?.resumo?.meta_percentual ?? 0}%</p>
        </div>
      </div>
    </Layout>
  );
}