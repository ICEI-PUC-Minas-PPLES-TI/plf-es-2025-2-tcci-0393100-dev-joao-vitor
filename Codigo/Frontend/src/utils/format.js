

export function formatCurrency(value) {
  const n = Number(value || 0);
  return n.toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

export function formatNumber(value, digits = 0) {
  const n = Number(value || 0);
  return n.toLocaleString("pt-BR", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

export function formatPercent(value, digits = 1) {
  const n = Number(value || 0);
  return `${n.toLocaleString("pt-BR", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  })}%`;
}

export function formatDateTime(value) {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return String(value);
  return d.toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

const STATUS_LABEL = {
  atingida: "Atingida",
  em_risco: "Em risco",
  nao_atingida: "Não atingida",
  importada: "Importada",
  validada: "Validada",
  validada_com_alertas: "Validada c/ alertas",
  processada: "Processada",
  erro: "Erro",
  valido: "Válido",
  invalido: "Inválido",
  pendente_validacao: "Pendente",
  encontrado: "Encontrado",
  nao_encontrado: "Não encontrado",
  ativo: "Ativo",
  inativo: "Inativo",
};

export function statusLabel(status) {
  return STATUS_LABEL[status] || status || "—";
}

/* Extrai mensagem de erro de uma resposta axios. */
export function errorMessage(err, fallback = "Ocorreu um erro inesperado.") {
  return (
    err?.response?.data?.detail ||
    err?.response?.data?.message ||
    err?.message ||
    fallback
  );
}
