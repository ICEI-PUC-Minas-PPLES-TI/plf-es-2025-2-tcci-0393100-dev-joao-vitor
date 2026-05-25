import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";
import api from "../api/client";

export default function KpiPage() {
  const [filters, setFilters] = useState({
    periodo_inicio: "",
    periodo_fim: "",
    regiao: "",
    categoria: "",
  });

  const [kpis, setKpis] = useState(null);
  const [message, setMessage] = useState("");

  const loadKpis = async () => {
    try {
      setMessage("");

      const params = {};

      Object.entries(filters).forEach(([key, value]) => {
        if (value) params[key] = value;
      });

      const { data } = await api.get("/kpis", { params });
      setKpis(data);
    } catch {
      setMessage("Erro ao carregar KPIs.");
    }
  };

  useEffect(() => {
    loadKpis();
  }, []);

  const handleChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <Layout>
      <div className="page-header">
        <h1>Indicadores de Desempenho</h1>
        <p>
          Consulta consolidada de KPIs por período, região e categoria.
        </p>
      </div>

      <div className="card">
        <h2>Filtros</h2>

        <div className="filter-grid">
          <input
            type="date"
            name="periodo_inicio"
            value={filters.periodo_inicio}
            onChange={handleChange}
          />

          <input
            type="date"
            name="periodo_fim"
            value={filters.periodo_fim}
            onChange={handleChange}
          />

          <input
            type="text"
            name="regiao"
            placeholder="Região"
            value={filters.regiao}
            onChange={handleChange}
          />

          <input
            type="text"
            name="categoria"
            placeholder="Categoria"
            value={filters.categoria}
            onChange={handleChange}
          />

          <button type="button" onClick={loadKpis}>
            Consultar KPIs
          </button>
        </div>

        {message && <div className="alert error">{message}</div>}
      </div>

      {kpis && (
        <>
          <div className="card">
            <h2>Resumo Geral</h2>

            <div className="stats-grid">
              <div className="stat-card">
                <span>Total de vendas</span>
                <h3>
                  R$ {kpis.resumo.total_vendas.toLocaleString("pt-BR")}
                </h3>
              </div>

              <div className="stat-card">
                <span>Quantidade vendida</span>
                <h3>{kpis.resumo.quantidade_total}</h3>
              </div>

              <div className="stat-card">
                <span>Total de pedidos</span>
                <h3>{kpis.resumo.total_pedidos}</h3>
              </div>

              <div className="stat-card">
                <span>Ticket médio</span>
                <h3>
                  R$ {kpis.resumo.ticket_medio.toLocaleString("pt-BR")}
                </h3>
              </div>
            </div>
          </div>

          <div className="card">
            <h2>KPIs por Região</h2>

            <table>
              <thead>
                <tr>
                  <th>Região</th>
                  <th>Total de vendas</th>
                  <th>Quantidade</th>
                  <th>Pedidos</th>
                  <th>Ticket médio</th>
                </tr>
              </thead>

              <tbody>
                {kpis.por_regiao.map((item) => (
                  <tr key={item.regiao}>
                    <td>{item.regiao}</td>
                    <td>R$ {item.total_vendas.toLocaleString("pt-BR")}</td>
                    <td>{item.quantidade_total}</td>
                    <td>{item.total_pedidos}</td>
                    <td>R$ {item.ticket_medio.toLocaleString("pt-BR")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="card">
            <h2>KPIs por Categoria</h2>

            <table>
              <thead>
                <tr>
                  <th>Categoria</th>
                  <th>Total de vendas</th>
                  <th>Quantidade</th>
                  <th>Pedidos</th>
                  <th>Ticket médio</th>
                </tr>
              </thead>

              <tbody>
                {kpis.por_categoria.map((item) => (
                  <tr key={item.categoria}>
                    <td>{item.categoria}</td>
                    <td>R$ {item.total_vendas.toLocaleString("pt-BR")}</td>
                    <td>{item.quantidade_total}</td>
                    <td>{item.total_pedidos}</td>
                    <td>R$ {item.ticket_medio.toLocaleString("pt-BR")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </Layout>
  );
}