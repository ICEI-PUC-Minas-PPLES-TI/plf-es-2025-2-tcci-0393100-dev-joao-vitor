"""Utilitários compartilhados pelos testes (geração de planilhas e vendas)."""

import io
from datetime import date

import pandas as pd

from app.db import models

COLUNAS = [
    "data_venda",
    "vendedor",
    "regiao",
    "produto",
    "categoria",
    "quantidade",
    "valor_unitario",
    "valor_total",
]


def construir_planilha(linhas: list[dict]) -> bytes:
    """Gera os bytes de um arquivo .xlsx a partir de uma lista de linhas."""

    df = pd.DataFrame(linhas, columns=COLUNAS)
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    return buffer.getvalue()


def linha_valida(**overrides) -> dict:
    """Retorna uma linha de venda válida, permitindo sobrescrever campos."""

    base = {
        "data_venda": "2025-01-15",
        "vendedor": "Carlos Souza",
        "regiao": "Sudeste",
        "produto": "Notebook Dell",
        "categoria": "Informática",
        "quantidade": 2,
        "valor_unitario": 1000.0,
        "valor_total": 2000.0,
    }
    base.update(overrides)
    return base


def semear_vendas(session, vendas: list[dict]) -> None:
    """Insere vendas diretamente na base (pré-condição de KPIs)."""

    for v in vendas:
        session.add(models.Venda(
            data_venda=v.get("data_venda", date(2025, 1, 15)),
            quantidade=v["quantidade"],
            valor_total=v["valor_total"],
            vendedor_nome=v.get("vendedor", "Carlos Souza"),
            regiao_nome=v["regiao"],
            produto_nome=v.get("produto", "Notebook Dell"),
            categoria_nome=v.get("categoria", "Informática"),
        ))
    session.commit()
