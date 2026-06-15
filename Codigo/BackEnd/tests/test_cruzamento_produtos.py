"""Testes unitários — cruzamento de produtos (UC10, CO11)."""

import io

import pandas as pd
import pytest

from app.services.cruzamento_produto_service import (
    CruzamentoProdutoService,
    SIMILARIDADE_MINIMA,
    calcular_similaridade,
)
from app.services.importacao_service import ImportacaoService
from app.services.validacao_planilha_service import ValidacaoPlanilhaService

LINHA_VALIDA = {
    "data_venda": "01/04/2026",
    "vendedor": "João",
    "regiao": "Sudeste",
    "produto": "Notebook Dell",
    "categoria": "Informática",
    "quantidade": 2,
    "valor_unitario": 3000,
    "valor_total": 6000,
}


def _gerar_excel(linhas):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame(linhas).to_excel(writer, index=False)
    buffer.seek(0)
    return buffer.getvalue()


def test_cruzamento_por_codigo_interno_exato(db_session):
    resultado = CruzamentoProdutoService(db_session).cruzar_produto("P001")

    assert resultado["status_cruzamento"] == "encontrado"
    assert resultado["confianca_cruzamento"] == 1.0
    assert resultado["produto_cadastrado"] == "Notebook Dell"


def test_cruzamento_por_descricao_exata(db_session):
    resultado = CruzamentoProdutoService(db_session).cruzar_produto("Notebook Dell")

    assert resultado["status_cruzamento"] == "encontrado"
    assert resultado["confianca_cruzamento"] >= SIMILARIDADE_MINIMA


def test_cruzamento_por_similaridade_com_erro_de_digitacao(db_session):
    resultado = CruzamentoProdutoService(db_session).cruzar_produto("Notebok Dell")

    assert resultado["status_cruzamento"] == "encontrado"
    assert resultado["confianca_cruzamento"] >= SIMILARIDADE_MINIMA


def test_cruzamento_nao_encontra_produto_desconhecido(db_session):
    resultado = CruzamentoProdutoService(db_session).cruzar_produto("Geladeira Brastemp XYZ")

    assert resultado["status_cruzamento"] == "nao_encontrado"
    assert resultado["produto_id"] is None


def test_similaridade_identicos_e_um():
    assert calcular_similaridade("Notebook Dell", "Notebook Dell") == 1.0


def test_similaridade_textos_distintos_e_baixa():
    assert calcular_similaridade("Mouse", "Cadeira de Escritório") < SIMILARIDADE_MINIMA


def test_similaridade_ignora_acentuacao_e_caixa():
    score = calcular_similaridade("teclado mecanico", "Teclado Mecânico")
    assert score >= SIMILARIDADE_MINIMA


def test_cruzamento_exige_planilha_validada(db_session, usuario):
    arquivo = _gerar_excel([LINHA_VALIDA])
    importacao = ImportacaoService(db_session).importar_planilha(
        arquivo, "vendas.xlsx", usuario
    )

    # Sem validar antes -> deve recusar
    with pytest.raises(ValueError):
        CruzamentoProdutoService(db_session).cruzar_produtos(importacao.id, usuario)


def test_cruzamento_completo_marca_status_processada(db_session, usuario):
    arquivo = _gerar_excel([LINHA_VALIDA])
    importacao = ImportacaoService(db_session).importar_planilha(
        arquivo, "vendas.xlsx", usuario
    )
    ValidacaoPlanilhaService(db_session).validar_planilha(importacao.id, usuario)

    resultado = CruzamentoProdutoService(db_session).cruzar_produtos(
        importacao.id, usuario
    )

    assert resultado["importacao"].status == "processada"
    assert resultado["criterio_similaridade_minima"] == SIMILARIDADE_MINIMA
    assert resultado["registros_processados"][0]["produto_cadastrado"] == "Notebook Dell"
