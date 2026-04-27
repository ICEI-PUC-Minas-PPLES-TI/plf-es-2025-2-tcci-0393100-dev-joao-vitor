import io
import pandas as pd
import pytest

from app.services.excel_service import (
    process_excel_file,
    cruzar_produto,
    calcular_similaridade,
)


def gerar_excel(dados):
    buffer = io.BytesIO()
    df = pd.DataFrame(dados)

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    buffer.seek(0)
    return buffer.getvalue()


def test_processa_planilha_valida_com_sucesso():
    arquivo = gerar_excel([
        {
            "data_venda": "01/04/2026",
            "vendedor": "João",
            "regiao": "Sudeste",
            "produto": "Notebook Dell",
            "categoria": "Informática",
            "quantidade": 2,
            "valor_unitario": 3000,
            "valor_total": 6000,
        }
    ])

    resultado = process_excel_file(arquivo)

    assert resultado["total_registros"] == 1
    assert resultado["total_validos"] == 1
    assert resultado["total_invalidos"] == 0
    assert resultado["registros"][0]["status_cruzamento"] == "encontrado"
    assert resultado["registros"][0]["produto_cadastrado"] == "Notebook Dell"


def test_identifica_coluna_obrigatoria_ausente():
    arquivo = gerar_excel([
        {
            "data_venda": "01/04/2026",
            "vendedor": "João",
            "regiao": "Sudeste",
            "produto": "Notebook Dell",
            "quantidade": 2,
            "valor_unitario": 3000,
            "valor_total": 6000,
        }
    ])

    with pytest.raises(ValueError) as erro:
        process_excel_file(arquivo)

    assert "Colunas obrigatórias ausentes" in str(erro.value)
    assert "categoria" in str(erro.value)


def test_identifica_registro_com_campos_invalidos():
    arquivo = gerar_excel([
        {
            "data_venda": "",
            "vendedor": "",
            "regiao": "Sudeste",
            "produto": "Notebook Dell",
            "categoria": "Informática",
            "quantidade": -1,
            "valor_unitario": 3000,
            "valor_total": 6000,
        }
    ])

    resultado = process_excel_file(arquivo)

    assert resultado["total_registros"] == 1
    assert resultado["total_validos"] == 0
    assert resultado["total_invalidos"] == 1

    erros = resultado["registros_invalidos"][0]["erros"]

    assert "data_venda ausente" in erros
    assert "vendedor ausente" in erros
    assert "quantidade deve ser maior que zero" in erros


def test_identifica_valor_total_incompativel():
    arquivo = gerar_excel([
        {
            "data_venda": "01/04/2026",
            "vendedor": "João",
            "regiao": "Sudeste",
            "produto": "Notebook Dell",
            "categoria": "Informática",
            "quantidade": 2,
            "valor_unitario": 3000,
            "valor_total": 1000,
        }
    ])

    resultado = process_excel_file(arquivo)

    assert resultado["total_invalidos"] == 1
    assert (
        "valor_total incompatível com quantidade x valor_unitario"
        in resultado["registros_invalidos"][0]["erros"]
    )


def test_identifica_registro_duplicado():
    linha = {
        "data_venda": "01/04/2026",
        "vendedor": "João",
        "regiao": "Sudeste",
        "produto": "Notebook Dell",
        "categoria": "Informática",
        "quantidade": 2,
        "valor_unitario": 3000,
        "valor_total": 6000,
    }

    arquivo = gerar_excel([linha, linha])

    resultado = process_excel_file(arquivo)

    assert resultado["total_registros"] == 2
    assert resultado["total_validos"] == 1
    assert resultado["total_invalidos"] == 1
    assert "registro duplicado" in resultado["registros_invalidos"][0]["erros"]


def test_cruzamento_produto_encontrado():
    resultado = cruzar_produto("Notebook Dell")

    assert resultado["status_cruzamento"] == "encontrado"
    assert resultado["produto_id"] == 1
    assert resultado["confianca_cruzamento"] >= 0.75


def test_cruzamento_produto_nao_encontrado():
    resultado = cruzar_produto("Produto Inexistente XYZ")

    assert resultado["status_cruzamento"] == "nao_encontrado"
    assert resultado["produto_id"] is None


def test_similaridade_textos_iguais():
    score = calcular_similaridade("Notebook Dell", "Notebook Dell")

    assert score == 1.0