import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";
import BarChart from "../components/BarChart";
import api from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { formatNumber, errorMessage } from "../utils/format";



export default function VendedorPage() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    async function load() {
      setLoading(true);
      setError("");
      try {
        const { data: resp } = await api.get("/dashboard/desempenho-individual");
        if (active) setData(resp);
      } catch (err) {
        if (active) setError(errorMessage(err));
      } finally {
        if (active) setLoading(false);
      }
    }
    load();
    return () => { active = false; };
  }, []);

  const resumo = data?.resumo;
  const porCategoria = (data?.por_categoria || []).map((c) => ({ label: c.categoria, value: c.total_vendas }));

  return (
    <Layout
      title="Meu Desempenho"
      crumb="Visão Geral"
      intro={`Acompanhe seus resultados individuais de vendas, ${user?.nome?.split(" ")[0] || ""}.`}
    >
      {error && <div className="note error">{error}</div>}

      {loading ? (
        <div className="panel"><span className="spinner" /> Carregando seu desempenho...</div>
      ) : (
        <>
          <div className="kpi-grid">
            <div className="kpi">
              <div className="label">Minhas Vendas</div>
              <div className="value"><span className="cur">R$</span>{formatNumber(resumo?.total_vendas, 2)}</div>
            </div>
            <div className="kpi teal">
              <div className="label">Quantidade</div>
              <div className="value">{formatNumber(resumo?.quantidade_total)}</div>
            </div>
            <div className="kpi info">
              <div className="label">Pedidos</div>
              <div className="value">{formatNumber(resumo?.total_pedidos)}</div>
            </div>
            <div className="kpi ok">
              <div className="label">Ticket Médio</div>
              <div className="value"><span className="cur">R$</span>{formatNumber(resumo?.ticket_medio, 2)}</div>
            </div>
          </div>

          <div className="panel">
            <div className="panel-head"><h2>Minhas Vendas por Categoria</h2></div>
            <BarChart
              data={porCategoria}
              emptyText="Você ainda não possui vendas registradas no período."
            />
          </div>
        </>
      )}
    </Layout>
  );
}
