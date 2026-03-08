import React, { useState } from "react";

const menuItems = [
  "Visão Geral",
  "KPIs",
  "Metas",
  "Alertas",
  "Relatórios",
  "Importação",
  "Validação",
  "Cruzamento",
  "Usuários",
  "IA",
];

export default function App() {
  const [paginaAtiva, setPaginaAtiva] = useState("Visão Geral");

  return (
    <div style={styles.app}>
      <aside style={styles.sidebar}>
        <div>
          <h1 style={styles.logo}>DashVendas</h1>
          <p style={styles.sidebarSubtitle}>Frontend em React</p>
        </div>

        <div style={styles.profileBox}>
          <p style={styles.profileLabel}>Projeto</p>
          <h3 style={styles.profileName}>DashVendas</h3>
          <p style={styles.profileText}>
            Protótipo funcional do sistema para análise de desempenho comercial,
            com foco em KPIs, metas, relatórios, importação de planilhas e apoio por IA.
          </p>
        </div>

        <nav style={styles.nav}>
          {menuItems.map((item) => (
            <button
              key={item}
              onClick={() => setPaginaAtiva(item)}
              style={paginaAtiva === item ? styles.navButtonActive : styles.navButton}
            >
              {item}
            </button>
          ))}
        </nav>

        <div style={styles.sidebarFooter}>
          <p style={styles.footerTitle}>Logo Aqui</p>
          <p style={styles.footerText}>
            Estrutura visual inicial 
          </p>
        </div>
      </aside>

      <main style={styles.main}>
        <header style={styles.header}>
          <div>
            <p style={styles.headerTag}>Sistema de análise comercial</p>
            <h2 style={styles.pageTitle}>{paginaAtiva}</h2>
          </div>

          <div style={styles.headerInfoBox}>
            <div style={styles.headerInfo}>08/03/2026</div>
            <div style={styles.headerInfo}>Protótipo funcional</div>
          </div>
        </header>

        {paginaAtiva === "Visão Geral" && <VisaoGeral />}
        {paginaAtiva === "KPIs" && <KPIs />}
        {paginaAtiva === "Metas" && <Metas />}
        {paginaAtiva === "Alertas" && <Alertas />}
        {paginaAtiva === "Relatórios" && <Relatorios />}
        {paginaAtiva === "Importação" && <Importacao />}
        {paginaAtiva === "Validação" && <Validacao />}
        {paginaAtiva === "Cruzamento" && <Cruzamento />}
        {paginaAtiva === "Usuários" && <Usuarios />}
        {paginaAtiva === "IA" && <IA />}
      </main>
    </div>
  );
}

function VisaoGeral() {
  return (
    <div style={styles.content}>
      <section style={styles.cardsGrid}>
        <Card title="Receita total" value="R$ 487.300" subtitle="+8,4% no período" />
        <Card title="Ticket médio" value="R$ 1.285" subtitle="+3,1% no período" />
        <Card title="Conversão" value="29,4%" subtitle="-1,2% no período" />
        <Card title="Meta atingida" value="76%" subtitle="+5,0% no período" />
      </section>

      <section style={styles.twoColumns}>
        <div style={styles.panel}>
          <h3 style={styles.panelTitle}>Desempenho comercial</h3>
          <p style={styles.panelSubtitle}>Resumo por vendedor, região e categoria.</p>

          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Vendedor</th>
                <th style={styles.th}>Região</th>
                <th style={styles.th}>Categoria</th>
                <th style={styles.th}>Valor</th>
                <th style={styles.th}>Status</th>
              </tr>
            </thead>
            <tbody>
              <TabelaLinha vendedor="Ana" regiao="Sudeste" categoria="Lajes" valor="R$ 82.400" status="Bom" />
              <TabelaLinha vendedor="Carlos" regiao="Centro-Oeste" categoria="Pré-moldados" valor="R$ 56.900" status="Atenção" />
              <TabelaLinha vendedor="Marina" regiao="Sul" categoria="Painéis" valor="R$ 97.100" status="Excelente" />
              <TabelaLinha vendedor="João" regiao="Nordeste" categoria="Lajes" valor="R$ 41.300" status="Risco" />
            </tbody>
          </table>
        </div>

        <div style={styles.panel}>
          <h3 style={styles.panelTitle}>Resumo executivo</h3>
          <p style={styles.panelSubtitle}>Síntese do comportamento comercial no período.</p>

          <div style={styles.highlightBox}>
            <p style={styles.highlightText}>
              O sistema apresenta crescimento mais consistente nas regiões Sudeste e Sul,
              enquanto o Nordeste demanda acompanhamento devido à queda de conversão e
              menor avanço sobre as metas previstas.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

function KPIs() {
  return (
    <div style={styles.content}>
      <section style={styles.cardsGrid}>
        <Card title="Receita total" value="R$ 487.300" subtitle="Indicador consolidado" />
        <Card title="Ticket médio" value="R$ 1.285" subtitle="Indicador consolidado" />
        <Card title="Conversão" value="29,4%" subtitle="Indicador consolidado" />
        <Card title="Meta atingida" value="76%" subtitle="Indicador consolidado" />
      </section>

      <div style={styles.panel}>
        <h3 style={styles.panelTitle}>Consulta de KPIs</h3>
        <p style={styles.panelSubtitle}>Visualização consolidada por período, região e categoria.</p>

        <div style={styles.filtersRow}>
          <input style={styles.input} placeholder="Período" />
          <input style={styles.input} placeholder="Região" />
          <input style={styles.input} placeholder="Categoria" />
          <button style={styles.primaryButton}>Filtrar</button>
        </div>

        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>Indicador</th>
              <th style={styles.th}>Período</th>
              <th style={styles.th}>Região</th>
              <th style={styles.th}>Categoria</th>
              <th style={styles.th}>Valor</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style={styles.td}>Receita total</td>
              <td style={styles.td}>Mar/2026</td>
              <td style={styles.td}>Sudeste</td>
              <td style={styles.td}>Lajes</td>
              <td style={styles.td}>R$ 184.200</td>
            </tr>
            <tr>
              <td style={styles.td}>Ticket médio</td>
              <td style={styles.td}>Mar/2026</td>
              <td style={styles.td}>Sul</td>
              <td style={styles.td}>Painéis</td>
              <td style={styles.td}>R$ 1.390</td>
            </tr>
            <tr>
              <td style={styles.td}>Conversão</td>
              <td style={styles.td}>Mar/2026</td>
              <td style={styles.td}>Nordeste</td>
              <td style={styles.td}>Lajes</td>
              <td style={styles.td}>21,4%</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Metas() {
  return (
    <div style={styles.content}>
      <div style={styles.twoColumns}>
        <div style={styles.panel}>
          <h3 style={styles.panelTitle}>Cadastro de metas</h3>
          <p style={styles.panelSubtitle}>Estrutura inicial do módulo de metas.</p>

          <div style={styles.formGrid}>
            <input style={styles.input} placeholder="Período" />
            <input style={styles.input} placeholder="Região" />
            <input style={styles.input} placeholder="Equipe" />
            <input style={styles.input} placeholder="Valor da meta" />
            <button style={styles.primaryButton}>Salvar meta</button>
          </div>
        </div>

        <div style={styles.panel}>
          <h3 style={styles.panelTitle}>Acompanhamento</h3>
          <p style={styles.panelSubtitle}>Classificação do progresso das equipes.</p>

          <MetaItem equipe="Equipe A" regiao="Sudeste" progresso={84} status="Em risco" />
          <MetaItem equipe="Equipe B" regiao="Sul" progresso={102} status="Atingida" />
          <MetaItem equipe="Equipe C" regiao="Nordeste" progresso={58} status="Não atingida" />
        </div>
      </div>
    </div>
  );
}

function Alertas() {
  return (
    <div style={styles.content}>
      <div style={styles.alertGrid}>
        <AlertaCard nivel="Crítico" titulo="Queda na conversão" mensagem="A conversão caiu 9% na região Nordeste." />
        <AlertaCard nivel="Atenção" titulo="Meta abaixo do esperado" mensagem="Equipe A apresenta avanço inferior ao planejado." />
        <AlertaCard nivel="Informativo" titulo="Relatório disponível" mensagem="O relatório consolidado de março foi gerado com sucesso." />
      </div>
    </div>
  );
}

function Relatorios() {
  return (
    <div style={styles.content}>
      <div style={styles.twoColumns}>
        <div style={styles.panel}>
          <h3 style={styles.panelTitle}>Gerar relatório</h3>
          <p style={styles.panelSubtitle}>Emissão sob demanda.</p>
          <div style={styles.formGrid}>
            <input style={styles.input} placeholder="Período" />
            <input style={styles.input} placeholder="Tipo de relatório" />
            <input style={styles.input} placeholder="Filtros gerais" />
            <button style={styles.primaryButton}>Gerar</button>
          </div>
        </div>

        <div style={styles.panel}>
          <h3 style={styles.panelTitle}>Agendamento</h3>
          <p style={styles.panelSubtitle}>Programação de relatórios periódicos.</p>
          <div style={styles.formGrid}>
            <input style={styles.input} placeholder="Periodicidade" />
            <input style={styles.input} placeholder="Destinatários" />
            <input style={styles.input} placeholder="Descrição" />
            <button style={styles.primaryButton}>Salvar agendamento</button>
          </div>
        </div>
      </div>
    </div>
  );
}

function Importacao() {
  return (
    <div style={styles.content}>
      <div style={styles.twoColumns}>
        <div style={styles.panel}>
          <h3 style={styles.panelTitle}>Importação de planilhas</h3>
          <p style={styles.panelSubtitle}>Envio de arquivos Excel para processamento.</p>
          <div style={styles.uploadBox}>
            <p style={styles.uploadTitle}>Selecione ou arraste um arquivo</p>
            <p style={styles.uploadText}>Formatos aceitos: .xls e .xlsx</p>
            <button style={styles.primaryButton}>Escolher arquivo</button>
          </div>
        </div>

        <div style={styles.panel}>
          <h3 style={styles.panelTitle}>Histórico de importações</h3>
          <p style={styles.panelSubtitle}>Últimos arquivos recebidos pelo sistema.</p>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Arquivo</th>
                <th style={styles.th}>Status</th>
                <th style={styles.th}>Linhas</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style={styles.td}>vendas_marco.xlsx</td>
                <td style={styles.td}><span style={getStatusStyle("Bom")}>Processado</span></td>
                <td style={styles.td}>1240</td>
              </tr>
              <tr>
                <td style={styles.td}>base_regioes.xlsx</td>
                <td style={styles.td}><span style={getStatusStyle("Atenção")}>Parcial</span></td>
                <td style={styles.td}>220</td>
              </tr>
              <tr>
                <td style={styles.td}>vendas_fev.xlsx</td>
                <td style={styles.td}><span style={getStatusStyle("Risco")}>Erro</span></td>
                <td style={styles.td}>980</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function Validacao() {
  return (
    <div style={styles.content}>
      <div style={styles.panel}>
        <h3 style={styles.panelTitle}>Validação automática</h3>
        <p style={styles.panelSubtitle}>Conferência de estrutura, campos obrigatórios e inconsistências.</p>

        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>Linha</th>
              <th style={styles.th}>Campo</th>
              <th style={styles.th}>Erro</th>
              <th style={styles.th}>Severidade</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style={styles.td}>14</td>
              <td style={styles.td}>Código interno</td>
              <td style={styles.td}>Campo ausente</td>
              <td style={styles.td}><span style={getStatusStyle("Crítico")}>Crítico</span></td>
            </tr>
            <tr>
              <td style={styles.td}>29</td>
              <td style={styles.td}>Valor total</td>
              <td style={styles.td}>Formato monetário inválido</td>
              <td style={styles.td}><span style={getStatusStyle("Atenção")}>Atenção</span></td>
            </tr>
            <tr>
              <td style={styles.td}>73</td>
              <td style={styles.td}>Produto</td>
              <td style={styles.td}>Registro duplicado</td>
              <td style={styles.td}><span style={getStatusStyle("Atenção")}>Atenção</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Cruzamento() {
  return (
    <div style={styles.content}>
      <div style={styles.panel}>
        <h3 style={styles.panelTitle}>Cruzamento de produtos</h3>
        <p style={styles.panelSubtitle}>Associação entre produtos da planilha e cadastro interno.</p>

        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>Código</th>
              <th style={styles.th}>Produto na planilha</th>
              <th style={styles.th}>Produto interno</th>
              <th style={styles.th}>Similaridade</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style={styles.td}>PL-001</td>
              <td style={styles.td}>Laje H8</td>
              <td style={styles.td}>Laje Treliçada H8</td>
              <td style={styles.td}>96%</td>
            </tr>
            <tr>
              <td style={styles.td}>PN-014</td>
              <td style={styles.td}>Painel Muro 2,20</td>
              <td style={styles.td}>Painel de Muro 2,20m</td>
              <td style={styles.td}>93%</td>
            </tr>
            <tr>
              <td style={styles.td}>LX-900</td>
              <td style={styles.td}>Produto não identificado</td>
              <td style={styles.td}>Sem correspondência</td>
              <td style={styles.td}>41%</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Usuarios() {
  return (
    <div style={styles.content}>
      <div style={styles.twoColumns}>
        <div style={styles.panel}>
          <h3 style={styles.panelTitle}>Usuários cadastrados</h3>
          <p style={styles.panelSubtitle}>Gestão de usuários do sistema.</p>

          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Nome</th>
                <th style={styles.th}>E-mail</th>
                <th style={styles.th}>Perfil</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style={styles.td}>Ana Silva</td>
                <td style={styles.td}>ana@dashvendas.com</td>
                <td style={styles.td}>Vendedor</td>
              </tr>
              <tr>
                <td style={styles.td}>Bruno Costa</td>
                <td style={styles.td}>bruno@dashvendas.com</td>
                <td style={styles.td}>Gestor</td>
              </tr>
              <tr>
                <td style={styles.td}>Clara Lima</td>
                <td style={styles.td}>clara@dashvendas.com</td>
                <td style={styles.td}>Analista</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div style={styles.panel}>
          <h3 style={styles.panelTitle}>Permissões</h3>
          <p style={styles.panelSubtitle}>Ajuste de perfil e privilégios.</p>

          <div style={styles.formGrid}>
            <input style={styles.input} placeholder="Usuário" />
            <input style={styles.input} placeholder="Perfil" />
            <input style={styles.input} placeholder="Permissão adicional" />
            <button style={styles.primaryButton}>Atualizar permissões</button>
          </div>
        </div>
      </div>
    </div>
  );
}

function IA() {
  return (
    <div style={styles.content}>
      <div style={styles.twoColumns}>
        <div style={styles.panel}>
          <h3 style={styles.panelTitle}>Análise interpretativa</h3>
          <p style={styles.panelSubtitle}>Síntese gerada a partir dos indicadores.</p>

          <div style={styles.highlightBox}>
            <p style={styles.highlightText}>
              A análise do período indica melhor desempenho no Sudeste e no Sul,
              com necessidade de ação corretiva no Nordeste devido à redução de conversão,
              menor avanço nas metas e maior incidência de alertas críticos.
            </p>
          </div>
        </div>

        <div style={styles.panel}>
          <h3 style={styles.panelTitle}>Pergunta em linguagem natural</h3>
          <p style={styles.panelSubtitle}>Interface inicial do assistente de IA.</p>

          <div style={styles.formGrid}>
            <textarea
              style={{ ...styles.input, minHeight: "120px", resize: "vertical" }}
              placeholder="Digite uma pergunta, por exemplo: Quais regiões exigem atenção imediata?"
            />
            <button style={styles.primaryButton}>Consultar IA</button>
          </div>
        </div>
      </div>
    </div>
  );
}

function Card({ title, value, subtitle }) {
  return (
    <div style={styles.card}>
      <p style={styles.cardTitle}>{title}</p>
      <h3 style={styles.cardValue}>{value}</h3>
      <p style={styles.cardSubtitle}>{subtitle}</p>
    </div>
  );
}

function TabelaLinha({ vendedor, regiao, categoria, valor, status }) {
  return (
    <tr>
      <td style={styles.td}>{vendedor}</td>
      <td style={styles.td}>{regiao}</td>
      <td style={styles.td}>{categoria}</td>
      <td style={styles.td}>{valor}</td>
      <td style={styles.td}>
        <span style={getStatusStyle(status)}>{status}</span>
      </td>
    </tr>
  );
}

function MetaItem({ equipe, regiao, progresso, status }) {
  return (
    <div style={styles.metaItem}>
      <div style={styles.metaHeader}>
        <div>
          <strong>{equipe}</strong>
          <p style={styles.metaRegion}>{regiao}</p>
        </div>
        <span style={getStatusStyle(status)}>{status}</span>
      </div>

      <div style={styles.progressBar}>
        <div style={{ ...styles.progressFill, width: `${Math.min(progresso, 100)}%` }} />
      </div>

      <p style={styles.metaProgress}>{progresso}% da meta alcançada</p>
    </div>
  );
}

function AlertaCard({ nivel, titulo, mensagem }) {
  return (
    <div style={styles.panel}>
      <div style={styles.alertHeader}>
        <h3 style={styles.panelTitle}>{titulo}</h3>
        <span style={getStatusStyle(nivel)}>{nivel}</span>
      </div>
      <p style={styles.panelSubtitle}>{mensagem}</p>
      <button style={styles.secondaryButton}>Ver detalhes</button>
    </div>
  );
}

function getStatusStyle(status) {
  const base = {
    padding: "6px 10px",
    borderRadius: "999px",
    fontSize: "12px",
    fontWeight: 600,
    display: "inline-block",
  };

  if (
    status === "Bom" ||
    status === "Excelente" ||
    status === "Atingida" ||
    status === "Processado"
  ) {
    return { ...base, background: "#dcfce7", color: "#166534" };
  }

  if (
    status === "Atenção" ||
    status === "Em risco" ||
    status === "Parcial"
  ) {
    return { ...base, background: "#fef3c7", color: "#92400e" };
  }

  if (
    status === "Risco" ||
    status === "Não atingida" ||
    status === "Crítico" ||
    status === "Erro"
  ) {
    return { ...base, background: "#fee2e2", color: "#991b1b" };
  }

  return { ...base, background: "#dbeafe", color: "#1d4ed8" };
}

const styles = {
  app: {
    minHeight: "100vh",
    background: "#f8fafc",
    color: "#0f172a",
    display: "grid",
    gridTemplateColumns: "280px 1fr",
  },
  sidebar: {
    background: "#ffffff",
    borderRight: "1px solid #e2e8f0",
    padding: "24px",
    display: "flex",
    flexDirection: "column",
    gap: "24px",
  },
  logo: {
    margin: 0,
    fontSize: "26px",
    fontWeight: 700,
  },
  sidebarSubtitle: {
    marginTop: "6px",
    color: "#64748b",
    fontSize: "14px",
  },
  profileBox: {
    background: "#f8fafc",
    border: "1px solid #e2e8f0",
    borderRadius: "16px",
    padding: "16px",
  },
  profileLabel: {
    margin: 0,
    fontSize: "12px",
    color: "#64748b",
    textTransform: "uppercase",
    letterSpacing: "0.08em",
  },
  profileName: {
    margin: "8px 0 6px 0",
    fontSize: "18px",
  },
  profileText: {
    margin: 0,
    color: "#475569",
    fontSize: "14px",
    lineHeight: 1.5,
  },
  nav: {
    display: "grid",
    gap: "10px",
  },
  navButton: {
    padding: "14px 16px",
    borderRadius: "14px",
    border: "1px solid #e2e8f0",
    background: "#ffffff",
    cursor: "pointer",
    textAlign: "left",
    fontSize: "14px",
    color: "#334155",
  },
  navButtonActive: {
    padding: "14px 16px",
    borderRadius: "14px",
    border: "1px solid #0f172a",
    background: "#0f172a",
    cursor: "pointer",
    textAlign: "left",
    fontSize: "14px",
    color: "#ffffff",
  },
  sidebarFooter: {
    marginTop: "auto",
    background: "#f8fafc",
    border: "1px solid #e2e8f0",
    borderRadius: "16px",
    padding: "16px",
  },
  footerTitle: {
    margin: 0,
    fontWeight: 700,
    fontSize: "14px",
  },
  footerText: {
    marginTop: "8px",
    marginBottom: 0,
    color: "#475569",
    fontSize: "14px",
    lineHeight: 1.5,
  },
  main: {
    padding: "32px",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    gap: "16px",
    flexWrap: "wrap",
  },
  headerTag: {
    margin: 0,
    color: "#64748b",
    textTransform: "uppercase",
    letterSpacing: "0.1em",
    fontSize: "12px",
    fontWeight: 600,
  },
  pageTitle: {
    marginTop: "10px",
    marginBottom: 0,
    fontSize: "34px",
  },
  headerInfoBox: {
    display: "flex",
    gap: "12px",
    flexWrap: "wrap",
  },
  headerInfo: {
    background: "#ffffff",
    border: "1px solid #e2e8f0",
    borderRadius: "12px",
    padding: "10px 14px",
    fontSize: "14px",
    color: "#475569",
  },
  content: {
    marginTop: "28px",
    display: "grid",
    gap: "20px",
  },
  cardsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: "16px",
  },
  card: {
    background: "#ffffff",
    border: "1px solid #e2e8f0",
    borderRadius: "18px",
    padding: "20px",
    boxShadow: "0 1px 2px rgba(0,0,0,0.04)",
  },
  cardTitle: {
    margin: 0,
    color: "#64748b",
    fontSize: "14px",
  },
  cardValue: {
    marginTop: "12px",
    marginBottom: "8px",
    fontSize: "30px",
  },
  cardSubtitle: {
    margin: 0,
    color: "#475569",
    fontSize: "13px",
  },
  twoColumns: {
    display: "grid",
    gridTemplateColumns: "2fr 1fr",
    gap: "20px",
  },
  panel: {
    background: "#ffffff",
    border: "1px solid #e2e8f0",
    borderRadius: "18px",
    padding: "22px",
    boxShadow: "0 1px 2px rgba(0,0,0,0.04)",
  },
  panelTitle: {
    marginTop: 0,
    marginBottom: "8px",
    fontSize: "20px",
  },
  panelSubtitle: {
    marginTop: 0,
    color: "#64748b",
    fontSize: "14px",
    lineHeight: 1.5,
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    marginTop: "18px",
  },
  th: {
    textAlign: "left",
    padding: "12px",
    background: "#f8fafc",
    color: "#475569",
    fontSize: "13px",
    borderBottom: "1px solid #e2e8f0",
  },
  td: {
    padding: "12px",
    borderBottom: "1px solid #e2e8f0",
    fontSize: "14px",
  },
  highlightBox: {
    marginTop: "16px",
    background: "#f8fafc",
    border: "1px solid #e2e8f0",
    borderRadius: "14px",
    padding: "16px",
  },
  highlightText: {
    margin: 0,
    color: "#475569",
    lineHeight: 1.6,
    fontSize: "14px",
  },
  filtersRow: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr 1fr auto",
    gap: "12px",
    marginTop: "18px",
    marginBottom: "18px",
  },
  input: {
    padding: "12px 14px",
    borderRadius: "12px",
    border: "1px solid #cbd5e1",
    fontSize: "14px",
    outline: "none",
    width: "100%",
  },
  primaryButton: {
    padding: "12px 16px",
    borderRadius: "12px",
    border: "1px solid #0f172a",
    background: "#0f172a",
    color: "#ffffff",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: 600,
  },
  secondaryButton: {
    padding: "12px 16px",
    borderRadius: "12px",
    border: "1px solid #cbd5e1",
    background: "#ffffff",
    color: "#0f172a",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: 600,
    marginTop: "12px",
  },
  formGrid: {
    display: "grid",
    gap: "12px",
    marginTop: "18px",
  },
  metaItem: {
    border: "1px solid #e2e8f0",
    borderRadius: "14px",
    padding: "16px",
    marginTop: "14px",
  },
  metaHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "12px",
  },
  metaRegion: {
    margin: "4px 0 0 0",
    color: "#64748b",
    fontSize: "14px",
  },
  progressBar: {
    width: "100%",
    height: "10px",
    background: "#e2e8f0",
    borderRadius: "999px",
    marginTop: "14px",
    overflow: "hidden",
  },
  progressFill: {
    height: "100%",
    background: "#0f172a",
    borderRadius: "999px",
  },
  metaProgress: {
    marginBottom: 0,
    color: "#475569",
    fontSize: "13px",
    marginTop: "8px",
  },
  alertGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(3, 1fr)",
    gap: "20px",
  },
  alertHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "12px",
  },
  uploadBox: {
    marginTop: "18px",
    border: "2px dashed #cbd5e1",
    borderRadius: "16px",
    padding: "32px",
    textAlign: "center",
    background: "#f8fafc",
  },
  uploadTitle: {
    margin: 0,
    fontWeight: 700,
    fontSize: "16px",
  },
  uploadText: {
    marginTop: "8px",
    marginBottom: "18px",
    color: "#64748b",
    fontSize: "14px",
  },
};