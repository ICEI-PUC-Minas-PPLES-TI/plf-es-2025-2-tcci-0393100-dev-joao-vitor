import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";
import BarChart from "../components/BarChart";
import api from "../api/client";
import {
  formatCurrency,
  formatNumber,
  errorMessage,
} from "../utils/format";

/* Indicadores (UC02 / CT01 / CT02).
   Permite filtrar por período, região e categoria e recalcula os KPIs. */

const EMPTY_FILTERS = {
  periodo_inicio: "",
  periodo_fim: "",
  regiao: "",
  categoria: "",
};

export default function KpiPage() {
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async (activeFilters) => {
    setLoading(true);
    setError("");
    try {
      const params = {};
      Object.entries(activeFilters).forEach(([key, value]) => {
        if (value) params[key] = value;
      });
      const { data: resp } = await api.get("/kpis", { params });
      setData(resp);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load(EMPTY_FILTERS);
  }, []);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  const handleApply = (event) => {
    event.preventDefault();
    load(filters);
  };

  const handleClear = () => {
    setFilters(EMPTY_FILTERS);
    load(EMPTY_FILTERS);
  };

  const resumo = data?.resumo;
  const porRegiao = (data?.por_regiao || []).map((r) => ({ label: r.regiao, value: r.total_vendas }));
  const porCategoria = (data?.por_categoria || []).map((c) => ({ label: c.categoria, value: c.total_vendas }));

  return (
    <Layout
      title="Indicadores de Desempenho"
      crumb="Análise"
      intro="Consulte os KPIs consolidados e aplique filtros por período, região e categoria."
    >
      {error && <div className="note error">{error}</div>}

      <div className="panel">
        <form className="toolbar" onSubmit={handleApply}>
          <div className="field">
            <label>Período inicial</label>
            <input type="date" name="periodo_inicio" value={filters.periodo_inicio} onChange={handleChange} />
          </div>
          <div className="field">
            <label>Período final</label>
            <input type="date" name="periodo_fim" value={filters.periodo_fim} onChange={handleChange} />
          </div>
          <div className="field">
            <label>Região</label>
            <input type="text" name="regiao" value={filters.regiao} onChange={handleChange} placeholder="Ex.: Sudeste" />
          </div>
          <div className="field">
            <label>Categoria</label>
            <input type="text" name="categoria" value={filters.categoria} onChange={handleChange} placeholder="Ex.: Informática" />
          </div>
          <button type="submit" className="btn btn-sm">Aplicar filtros</button>
          <button type="button" className="btn btn-ghost btn-sm" onClick={handleClear}>Limpar</button>
        </form>
      </div>

      {loading ? (
        <div className="panel"><span className="spinner" /> Calculando indicadores...</div>
      ) : (
        <>
          <div className="kpi-grid" style={{ marginTop: 20 }}>
            <div className="kpi">
              <div className="label">Total de Vendas</div>
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
            <div className="panel-head">
              <h2>Vendas por Região</h2>
              <span className="hint">{data?.total_registros_considerados || 0} registros considerados</span>
            </div>
            <BarChart data={porRegiao} />
          </div>

          <div className="panel">
            <div className="panel-head"><h2>Vendas por Categoria</h2></div>
            <BarChart data={porCategoria} />
          </div>

          <div className="panel">
            <div className="panel-head"><h2>Desempenho por Vendedor</h2></div>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Vendedor</th>
                    <th className="num">Total de Vendas</th>
                    <th className="num">Pedidos</th>
                    <th className="num">Ticket Médio</th>
                  </tr>
                </thead>
                <tbody>
                  {(data?.por_vendedor || []).length === 0 ? (
                    <tr><td className="table-empty" colSpan={4}>Nenhum dado de vendedor para os filtros aplicados.</td></tr>
                  ) : (
                    data.por_vendedor.map((v) => (
                      <tr key={v.vendedor}>
                        <td className="strong">{v.vendedor}</td>
                        <td className="num">{formatCurrency(v.total_vendas)}</td>
                        <td className="num">{formatNumber(v.total_pedidos)}</td>
                        <td className="num">{formatCurrency(v.ticket_medio)}</td>
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
