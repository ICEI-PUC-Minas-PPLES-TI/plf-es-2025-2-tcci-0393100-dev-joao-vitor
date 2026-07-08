"""Testes unitários — validação de planilha (UC09, Template Method).

Cobrem o detalhamento das regras de validação executadas pelo método
validar_item() e o fluxo fixo do Template Method validar_planilha().
"""

import io

import pandas as pd
import pytest

from app.services.importacao_service import ImportacaoService
from app.services.validacao_planilha_service import (
    ValidacaoPlanilhaService,
    ValidacaoPlanilhaTemplate,
)

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


def _importar(db, usuario, linhas):
    arquivo = _gerar_excel(linhas)
    return ImportacaoService(db).importar_planilha(arquivo, "vendas.xlsx", usuario)


def test_validar_item_aceita_linha_correta(db_session):
    service = ValidacaoPlanilhaService(db_session)
    assert service.validar_item(LINHA_VALIDA) == []


def test_validar_item_detecta_campos_textuais_ausentes(db_session):
    service = ValidacaoPlanilhaService(db_session)
    linha = dict(LINHA_VALIDA)
    linha["vendedor"] = ""
    linha["regiao"] = None

    erros = service.validar_item(linha)
    assert "vendedor ausente" in erros
    assert "regiao ausente" in erros


def test_validar_item_detecta_numero_negativo_e_zero(db_session):
    service = ValidacaoPlanilhaService(db_session)

    linha_zero = dict(LINHA_VALIDA)
    linha_zero["quantidade"] = 0
    assert "quantidade deve ser maior que zero" in service.validar_item(linha_zero)

    linha_neg = dict(LINHA_VALIDA)
    linha_neg["valor_unitario"] = -10
    assert "valor_unitario deve ser maior que zero" in service.validar_item(linha_neg)


def test_validar_item_detecta_valor_total_incompativel(db_session):
    service = ValidacaoPlanilhaService(db_session)
    linha = dict(LINHA_VALIDA)
    linha["valor_total"] = 5000  # 2 x 3000 = 6000, não 5000

    erros = service.validar_item(linha)
    assert "valor_total incompatível com quantidade x valor_unitario" in erros


def test_validar_item_aceita_tolerancia_de_arredondamento(db_session):
    service = ValidacaoPlanilhaService(db_session)
    linha = dict(LINHA_VALIDA)
    linha["quantidade"] = 3
    linha["valor_unitario"] = 33.33
    linha["valor_total"] = 99.99  # 3 x 33.33 = 99.99

    assert service.validar_item(linha) == []


def test_validar_item_detecta_data_invalida(db_session):
    service = ValidacaoPlanilhaService(db_session)
    linha = dict(LINHA_VALIDA)
    linha["data_venda"] = "data_qualquer"

    assert "data_venda inválida" in service.validar_item(linha)


def test_template_method_detecta_duplicados(db_session, usuario):
    importacao = _importar(db_session, usuario, [LINHA_VALIDA, dict(LINHA_VALIDA)])

    resultado = ValidacaoPlanilhaService(db_session).validar_planilha(
        importacao.id, usuario
    )

    assert resultado["total_registros"] == 2
    assert resultado["total_validos"] == 1
    assert resultado["total_invalidos"] == 1
    # A mensagem inclui a linha de origem (ex.: "registro duplicado (igual à linha 2)").
    erros = resultado["registros_invalidos"][0]["erros"]
    assert any("registro duplicado" in e for e in erros)


def test_template_method_falha_sem_itens(db_session, usuario):
    from app.db import models

    importacao = models.Importacao(
        nome_arquivo="vazia.xlsx", status="importada", id_usuario=usuario.id
    )
    db_session.add(importacao)
    db_session.commit()

    with pytest.raises(ValueError):
        ValidacaoPlanilhaService(db_session).validar_planilha(importacao.id, usuario)


def test_template_method_pode_ser_especializado(db_session):
    """O hook validar_item() pode ser sobrescrito (extensibilidade)."""

    class ValidacaoEstrita(ValidacaoPlanilhaTemplate):
        def validar_item(self, dados):
            erros = super().validar_item(dados)
            if float(dados.get("valor_total", 0)) > 5000:
                erros.append("valor acima do limite permitido")
            return erros

    service = ValidacaoEstrita(db_session)
    erros = service.validar_item(LINHA_VALIDA)
    assert "valor acima do limite permitido" in erros
