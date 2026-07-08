import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";
import api from "../api/client";
import { formatDateTime, errorMessage } from "../utils/format";

/* Alertas (UC05).
   Lista os alertas de desempenho gerados automaticamente a partir das
   metas em risco/não atingidas e permite marcá-los como lidos. */

export default function AlertasPage() {
  const [alertas, setAlertas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [onlyUnread, setOnlyUnread] = useState(false);

  const load = async (apenasNaoLidos) => {
    setLoading(true);
    setError("");
    try {
      const { data } = await api.get("/alertas", {
        params: { apenas_nao_lidos: apenasNaoLidos },
      });
      setAlertas(data);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load(onlyUnread);
  }, [onlyUnread]);

  const marcarLido = async (id) => {
    try {
      await api.patch(`/alertas/${id}/lido`);
      load(onlyUnread);
    } catch (err) {
      setError(errorMessage(err));
    }
  };

  const naoLidos = alertas.filter((a) => !a.lido).length;

  return (
    <Layout
      title="Alertas de Desempenho"
      crumb="Análise"
      intro="O sistema monitora as metas e gera alertas quando há risco de desempenho abaixo do esperado."
      actions={
        <button className="btn btn-ghost btn-sm" onClick={() => load(onlyUnread)}>
          Atualizar alertas
        </button>
      }
    >
      {error && <div className="note error">{error}</div>}

      <div className="panel">
        <div className="panel-head">
          <h2>Alertas {naoLidos > 0 && <span className="badge warn">{naoLidos} não lido(s)</span>}</h2>
          <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: "0.85rem", color: "var(--text-2)" }}>
            <input
              type="checkbox"
              checked={onlyUnread}
              onChange={(e) => setOnlyUnread(e.target.checked)}
              style={{ width: "auto" }}
            />
            Mostrar apenas não lidos
          </label>
        </div>

        {loading ? (
          <div><span className="spinner" /> Carregando alertas...</div>
        ) : alertas.length === 0 ? (
          <p className="chat-empty" style={{ margin: "32px 0" }}>
            Nenhum alerta no momento. As metas estão sob controle.
          </p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Criticidade</th>
                  <th>Mensagem</th>
                  <th>Período</th>
                  <th>Gerado em</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {alertas.map((a) => (
                  <tr key={a.id} style={{ opacity: a.lido ? 0.55 : 1 }}>
                    <td><span className={`pill-level ${a.nivel_criticidade}`}>{a.nivel_criticidade}</span></td>
                    <td className="strong">{a.mensagem}</td>
                    <td>{a.periodo_referencia || "—"}</td>
                    <td>{formatDateTime(a.created_at)}</td>
                    <td>
                      {a.lido ? (
                        <span className="badge muted">Lido</span>
                      ) : (
                        <button className="btn btn-ghost btn-sm" onClick={() => marcarLido(a.id)}>
                          Marcar como lido
                        </button>
                      )}
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
