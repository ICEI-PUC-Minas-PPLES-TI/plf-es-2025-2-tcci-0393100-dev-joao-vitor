from datetime import datetime
from typing import Optional

import app.services.mock_db as mock_db


def _parse_date(value):
    if not value:
        return None

    if isinstance(value, datetime):
        return value.date()

    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except ValueError:
        return None


def _filtrar_vendas(
    periodo_inicio: Optional[str] = None,
    periodo_fim: Optional[str] = None,
    regiao: Optional[str] = None,
    categoria: Optional[str] = None,
):
    inicio = _parse_date(periodo_inicio)
    fim = _parse_date(periodo_fim)

    vendas_filtradas = []

    for venda in mock_db.mock_sales_data:
        data_venda = _parse_date(venda.get("data_venda"))

        if inicio and data_venda and data_venda < inicio:
            continue

        if fim and data_venda and data_venda > fim:
            continue

        if regiao and venda.get("regiao", "").lower() != regiao.lower():
            continue

        if categoria and venda.get("categoria", "").lower() != categoria.lower():
            continue

        vendas_filtradas.append(venda)

    return vendas_filtradas


def _calcular_resumo(vendas):
    total_vendas = sum(float(venda.get("valor_total", 0) or 0) for venda in vendas)
    quantidade_total = sum(float(venda.get("quantidade", 0) or 0) for venda in vendas)
    total_pedidos = len(vendas)
    ticket_medio = total_vendas / total_pedidos if total_pedidos else 0

    return {
        "total_vendas": round(total_vendas, 2),
        "quantidade_total": round(quantidade_total, 2),
        "total_pedidos": total_pedidos,
        "ticket_medio": round(ticket_medio, 2),
    }


def _agrupar_por(vendas, campo):
    grupos = {}

    for venda in vendas:
        chave = venda.get(campo) or "Não informado"

        if chave not in grupos:
            grupos[chave] = []

        grupos[chave].append(venda)

    return [
        {
            campo: chave,
            **_calcular_resumo(lista_vendas),
        }
        for chave, lista_vendas in grupos.items()
    ]


def consultar_kpis(
    periodo_inicio: Optional[str] = None,
    periodo_fim: Optional[str] = None,
    regiao: Optional[str] = None,
    categoria: Optional[str] = None,
):
    vendas = _filtrar_vendas(
        periodo_inicio=periodo_inicio,
        periodo_fim=periodo_fim,
        regiao=regiao,
        categoria=categoria,
    )

    return {
        "filtros": {
            "periodo_inicio": periodo_inicio,
            "periodo_fim": periodo_fim,
            "regiao": regiao,
            "categoria": categoria,
        },
        "resumo": _calcular_resumo(vendas),
        "por_regiao": _agrupar_por(vendas, "regiao"),
        "por_categoria": _agrupar_por(vendas, "categoria"),
        "total_registros_considerados": len(vendas),
    }