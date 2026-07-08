import React from "react";
import { formatCurrency } from "../utils/format";

/* Gráfico de barras horizontais em CSS puro (sem libs).
   data: [{ label, value }]  — usa a maior barra como 100%. */
export default function BarChart({ data, valueFormatter = formatCurrency, emptyText = "Sem dados para exibir." }) {
  const rows = (data || []).filter((d) => d && d.label != null);

  if (rows.length === 0) {
    return <p className="chat-empty" style={{ margin: "24px 0" }}>{emptyText}</p>;
  }

  const max = Math.max(...rows.map((r) => Number(r.value) || 0), 1);

  return (
    <div className="bars">
      {rows.map((row) => {
        const value = Number(row.value) || 0;
        const pct = Math.max((value / max) * 100, 2);
        return (
          <div className="bar-row" key={row.label}>
            <div className="bl" title={row.label}>{row.label}</div>
            <div className="bar-track">
              <div className="bar-fill" style={{ width: `${pct}%` }} />
            </div>
            <div className="bv">{valueFormatter(value)}</div>
          </div>
        );
      })}
    </div>
  );
}
