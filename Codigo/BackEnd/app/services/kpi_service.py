"""KPIService — cálculo de indicadores de desempenho.

Conforme a Seção 3.4 da documentação, o cálculo dos KPIs adota o
padrão Strategy: o método calcular_kpis() delega o processamento a
estratégias específicas de cálculo, permitindo que novos indicadores
sejam incluídos sem modificar o fluxo principal (princípio Open/Closed).
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.repositories import VendaRepository


# ---------------------------------------------------------------------------
# Padrão Strategy — estratégias de cálculo de KPI
# ---------------------------------------------------------------------------

class KPIStrategy(ABC):
    """Interface das estratégias de cálculo de KPI."""

    nome: str

    @abstractmethod
    def calcular(self, vendas: list) -> float:
        ...


class TotalVendasStrategy(KPIStrategy):
    nome = "total_vendas"

    def calcular(self, vendas: list) -> float:
        return round(sum(float(v.valor_total or 0) for v in vendas), 2)


class QuantidadeTotalStrategy(KPIStrategy):
    nome = "quantidade_total"

    def calcular(self, vendas: list) -> float:
        return round(sum(float(v.quantidade or 0) for v in vendas), 2)


class TotalPedidosStrategy(KPIStrategy):
    nome = "total_pedidos"

    def calcular(self, vendas: list) -> float:
        return len(vendas)


class TicketMedioStrategy(KPIStrategy):
    nome = "ticket_medio"

    def calcular(self, vendas: list) -> float:
        total = sum(float(v.valor_total or 0) for v in vendas)
        pedidos = len(vendas)
        return round(total / pedidos, 2) if pedidos else 0.0


ESTRATEGIAS_PADRAO: list[KPIStrategy] = [
    TotalVendasStrategy(),
    QuantidadeTotalStrategy(),
    TotalPedidosStrategy(),
    TicketMedioStrategy(),
]


# ---------------------------------------------------------------------------
# Serviço
# ---------------------------------------------------------------------------

def _parse_date(value):
    if not value:
        return None

    if isinstance(value, datetime):
        return value.date()

    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except ValueError:
        return None


class KPIService:
    def __init__(self, db: Session, estrategias: Optional[list[KPIStrategy]] = None):
        self.venda_repository = VendaRepository(db)
        self.estrategias = estrategias or ESTRATEGIAS_PADRAO

    def _calcular_resumo(self, vendas: list) -> dict:
        resumo = {}
        for estrategia in self.estrategias:
            resumo[estrategia.nome] = estrategia.calcular(vendas)
        return resumo

    def _agrupar_por(self, vendas: list, campo_entidade: str, campo_saida: str) -> list[dict]:
        grupos: dict[str, list] = {}

        for venda in vendas:
            chave = getattr(venda, campo_entidade) or "Não informado"
            grupos.setdefault(chave, []).append(venda)

        return [
            {campo_saida: chave, **self._calcular_resumo(lista)}
            for chave, lista in grupos.items()
        ]

    def calcular_kpis(
        self,
        periodo_inicio: Optional[str] = None,
        periodo_fim: Optional[str] = None,
        regiao: Optional[str] = None,
        categoria: Optional[str] = None,
        vendedor: Optional[str] = None,
    ) -> dict:
        """Consulta as vendas consolidadas e calcula os KPIs (CO02)."""

        vendas = self.venda_repository.consultar(
            periodo_inicio=_parse_date(periodo_inicio),
            periodo_fim=_parse_date(periodo_fim),
            regiao=regiao,
            categoria=categoria,
            vendedor=vendedor,
        )

        return {
            "filtros": {
                "periodo_inicio": periodo_inicio,
                "periodo_fim": periodo_fim,
                "regiao": regiao,
                "categoria": categoria,
                "vendedor": vendedor,
            },
            "resumo": self._calcular_resumo(vendas),
            "por_regiao": self._agrupar_por(vendas, "regiao_nome", "regiao"),
            "por_categoria": self._agrupar_por(vendas, "categoria_nome", "categoria"),
            "por_vendedor": self._agrupar_por(vendas, "vendedor_nome", "vendedor"),
            "total_registros_considerados": len(vendas),
        }
