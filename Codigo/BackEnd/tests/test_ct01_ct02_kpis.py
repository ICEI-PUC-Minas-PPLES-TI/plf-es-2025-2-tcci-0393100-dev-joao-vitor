"""Casos de Teste de Aceitação CT01 e CT02 — Visualização de KPIs.

Referência: Seção 6.1 da Documentação de Projeto (Tabelas 7 e 8).

CT01 - Visualizar KPIs Consolidados (Cenário Básico):
    valida que o sistema calcula e exibe os KPIs consolidados
    (total de vendas, total de pedidos, ticket médio) a partir das
    vendas persistidas, com valores numéricos coerentes.

CT02 - Visualizar KPIs Consolidados (Filtro por Região):
    valida que o sistema filtra corretamente os KPIs por região e
    recalcula os indicadores apenas para o subconjunto selecionado.

Sistemas envolvidos: KPIService, VendaRepository.
"""

from app.services.kpi_service import KPIService
from tests._helpers import semear_vendas


class TestCT01KpisConsolidados:
    """CT01 - Cenário básico de KPIs consolidados."""

    def test_kpis_consolidados_valores_coerentes(self, db_session):
        # Pré-condição: base contendo registros de vendas válidos.
        semear_vendas(db_session, [
            {"regiao": "Sudeste", "quantidade": 2, "valor_total": 2000.0},
            {"regiao": "Sul", "quantidade": 3, "valor_total": 1500.0},
            {"regiao": "Nordeste", "quantidade": 1, "valor_total": 500.0},
        ])

        # Passo: o sistema carrega/calcula os KPIs.
        resultado = KPIService(db_session).calcular_kpis()
        resumo = resultado["resumo"]

        # Resultado esperado: valores numéricos coerentes com o cadastrado.
        assert resumo["total_vendas"] == 4000.0
        assert resumo["quantidade_total"] == 6.0
        assert resumo["total_pedidos"] == 3
        assert resumo["ticket_medio"] == round(4000.0 / 3, 2)
        assert resultado["total_registros_considerados"] == 3

    def test_ticket_medio_zero_sem_vendas(self, db_session):
        # Sem vendas, o ticket médio deve ser 0 (sem divisão por zero).
        resultado = KPIService(db_session).calcular_kpis()
        assert resultado["resumo"]["total_pedidos"] == 0
        assert resultado["resumo"]["ticket_medio"] == 0.0

    def test_kpis_agrupados_por_regiao_existem(self, db_session):
        semear_vendas(db_session, [
            {"regiao": "Sudeste", "quantidade": 2, "valor_total": 2000.0},
            {"regiao": "Sul", "quantidade": 3, "valor_total": 1500.0},
        ])
        resultado = KPIService(db_session).calcular_kpis()
        regioes = {r["regiao"] for r in resultado["por_regiao"]}
        assert regioes == {"Sudeste", "Sul"}


class TestCT02KpisFiltroPorRegiao:
    """CT02 - Filtro por região recalcula os indicadores."""

    def test_filtro_por_regiao_recalcula_kpis(self, db_session):
        # Pré-condição: registros de vendas para diferentes regiões.
        semear_vendas(db_session, [
            {"regiao": "Sudeste", "quantidade": 2, "valor_total": 2000.0},
            {"regiao": "Sudeste", "quantidade": 1, "valor_total": 1000.0},
            {"regiao": "Sul", "quantidade": 3, "valor_total": 1500.0},
        ])

        # Ação: o usuário escolhe a região e solicita atualização.
        resultado = KPIService(db_session).calcular_kpis(regiao="Sudeste")

        # Resultado esperado: KPIs referentes apenas à região filtrada.
        assert resultado["resumo"]["total_vendas"] == 3000.0
        assert resultado["resumo"]["total_pedidos"] == 2
        assert resultado["total_registros_considerados"] == 2
        assert resultado["filtros"]["regiao"] == "Sudeste"

    def test_filtro_regiao_sem_correspondencia(self, db_session):
        semear_vendas(db_session, [
            {"regiao": "Sudeste", "quantidade": 2, "valor_total": 2000.0},
        ])
        resultado = KPIService(db_session).calcular_kpis(regiao="Norte")
        assert resultado["resumo"]["total_vendas"] == 0
        assert resultado["resumo"]["total_pedidos"] == 0

    def test_filtro_por_categoria(self, db_session):
        semear_vendas(db_session, [
            {"regiao": "Sudeste", "categoria": "Informática", "quantidade": 2, "valor_total": 2000.0},
            {"regiao": "Sul", "categoria": "Móveis", "quantidade": 1, "valor_total": 800.0},
        ])
        resultado = KPIService(db_session).calcular_kpis(categoria="Móveis")
        assert resultado["resumo"]["total_vendas"] == 800.0
        assert resultado["resumo"]["total_pedidos"] == 1
