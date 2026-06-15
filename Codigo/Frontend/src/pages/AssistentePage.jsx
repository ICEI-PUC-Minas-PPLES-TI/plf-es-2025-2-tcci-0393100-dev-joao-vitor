import React, { useEffect, useRef, useState } from "react";
import Layout from "../components/Layout";
import api from "../api/client";
import { errorMessage } from "../utils/format";

/* Assistente IA (UC12 / UC13).
   - UC12: análise interpretativa do desempenho (POST /assistente/analise).
   - UC13: perguntas em linguagem natural (POST /assistente/perguntar).
   O backend usa a GPT API quando configurada (OPENAI_API_KEY) e, caso
   contrário, gera respostas localmente a partir dos KPIs reais. */

const SUGESTOES = [
  "Qual o total de vendas?",
  "Qual a melhor região?",
  "Como estão as metas?",
  "Qual o melhor vendedor?",
];

export default function AssistentePage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const chatRef = useRef(null);

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const pushMessage = (msg) => setMessages((prev) => [...prev, msg]);

  const enviarPergunta = async (pergunta) => {
    const texto = (pergunta ?? input).trim();
    if (!texto || loading) return;

    setError("");
    pushMessage({ role: "user", text: texto });
    setInput("");
    setLoading(true);

    try {
      const { data } = await api.post("/assistente/perguntar", { pergunta: texto });
      pushMessage({ role: "bot", text: data.resposta, provedor: data.provedor });
    } catch (err) {
      setError(errorMessage(err));
      pushMessage({
        role: "bot",
        text: "Não consegui responder agora. Verifique se há dados de vendas e tente novamente.",
        provedor: "erro",
      });
    } finally {
      setLoading(false);
    }
  };

  const gerarAnalise = async () => {
    if (loading) return;
    setError("");
    pushMessage({ role: "user", text: "Gerar análise geral do desempenho." });
    setLoading(true);
    try {
      const { data } = await api.post("/assistente/analise", {});
      pushMessage({ role: "bot", text: data.resposta, provedor: data.provedor });
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    enviarPergunta();
  };

  return (
    <Layout
      title="Assistente de IA"
      crumb="Análise"
      intro="Faça perguntas em linguagem natural sobre o desempenho comercial ou gere uma análise interpretativa completa."
      actions={
        <button className="btn btn-sm" onClick={gerarAnalise} disabled={loading}>
          Gerar análise geral
        </button>
      }
    >
      {error && <div className="note error">{error}</div>}

      <div className="panel">
        <div className="suggest">
          {SUGESTOES.map((s) => (
            <button key={s} onClick={() => enviarPergunta(s)} disabled={loading}>
              {s}
            </button>
          ))}
        </div>

        <div className="chat" ref={chatRef}>
          {messages.length === 0 && !loading ? (
            <div className="chat-empty">
              Comece perguntando algo como "Qual o total de vendas?" ou clique em
              "Gerar análise geral".
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={idx} className={`msg ${msg.role}`}>
                {msg.text}
                {msg.role === "bot" && msg.provedor && (
                  <span className="prov">
                    {msg.provedor === "local"
                      ? "análise local"
                      : msg.provedor === "erro"
                      ? "indisponível"
                      : `via ${msg.provedor}`}
                  </span>
                )}
              </div>
            ))
          )}
          {loading && (
            <div className="msg bot">
              <span className="spinner" /> Analisando...
            </div>
          )}
        </div>

        <form className="chat-form" onSubmit={handleSubmit}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Digite uma mensagem..."
            disabled={loading}
          />
          <button type="submit" className="btn" disabled={loading || !input.trim()}>
            Enviar
          </button>
        </form>
      </div>
    </Layout>
  );
}
