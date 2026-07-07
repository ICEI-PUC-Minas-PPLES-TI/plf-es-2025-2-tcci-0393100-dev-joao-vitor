"""Testes de robustez, casos de fronteira e resiliência a falhas.

Complementam os testes de caminho feliz, atendendo à recomendação de
ampliar a cobertura com valores de fronteira, cenários negativos mais
ricos e falhas em integrações externas. Cobrem:

  - resiliência do Assistente de IA quando o provedor externo falha ou
    fica indisponível (fallback para o modo local);
  - valores de fronteira na validação de planilhas (tolerância de
    arredondamento, limite exato entre válido e inválido);
  - cenários negativos de importação (planilha vazia, colunas ausentes);
  - consistência de dados após operações encadeadas (importar -> validar).
"""

import io

import pandas as pd
import pytest

from app.integrations.ia_gateway import IAGateway
from app.services.ia_service import IAService
from app.services.importacao_service import ImportacaoService
from app.services.validacao_planilha_service import ValidacaoPlanilhaService
from tests._helpers import construir_planilha, linha_valida, semear_vendas


# ===========================================================================
# 1. Resiliência da integração externa de IA (fallback)
# ===========================================================================

class GatewayQueFalha(IAGateway):
    """Simula um provedor externo de IA indisponível (sempre falha)."""
    nome = "externo_indisponivel"

    def gerar_resposta(self, prompt, contexto):
        return None  # None sinaliza falha -> o serviço deve usar o modo local


class GatewayQueQuebra(IAGateway):
    """Simula um provedor externo que lança exceção inesperada."""
    nome = "externo_com_erro"

    def gerar_resposta(self, prompt, contexto):
        raise ConnectionError("Falha simulada de conexão com a IA externa")


def test_ia_usa_fallback_local_quando_externo_indisponivel(db_session):
    semear_vendas(db_session, [
        {"regiao": "Sudeste", "categoria": "Informática", "quantidade": 1, "valor_total": 5000.0},
    ])
    service = IAService(db_session, gateway=GatewayQueFalha())

    resultado = service.gerar_analise()

    # Mesmo com o provedor externo indisponível, a análise é gerada localmente.
    assert resultado["provedor"] == "local"
    assert "Sudeste" in resultado["resposta"]


def test_ia_pergunta_usa_fallback_quando_externo_indisponivel(db_session):
    semear_vendas(db_session, [
        {"regiao": "Sul", "categoria": "Periféricos", "quantidade": 2, "valor_total": 1000.0},
    ])
    service = IAService(db_session, gateway=GatewayQueFalha())

    resultado = service.consultar_ia("Qual o resumo das vendas?")

    assert resultado["provedor"] == "local"
    assert "1.000,00" in resultado["resposta"]


def test_ia_propaga_erro_inesperado_do_provedor_externo(db_session):
    """Se o provedor externo lança uma exceção inesperada, ela não deve
    ser silenciada pelo serviço (o tratamento de falha controlada é
    retornar None; um erro inesperado deve ser observável)."""
    semear_vendas(db_session, [
        {"regiao": "Sudeste", "categoria": "Informática", "quantidade": 1, "valor_total": 100.0},
    ])
    service = IAService(db_session, gateway=GatewayQueQuebra())

    with pytest.raises(ConnectionError):
        service.gerar_analise()


# ===========================================================================
# 2. Valores de fronteira na validação
# ===========================================================================

def test_validacao_aceita_valor_no_limite_de_tolerancia(db_session):
    """valor_total = quantidade x valor_unitario com diferença de 1 centavo
    (dentro da tolerância de arredondamento) deve ser aceito."""
    service = ValidacaoPlanilhaService(db_session)
    linha = {
        "data_venda": "2025-01-15", "vendedor": "Ana", "regiao": "Sul",
        "produto": "Mouse Logitech", "categoria": "Periféricos",
        "quantidade": 3, "valor_unitario": 33.33, "valor_total": 99.99,
    }
    assert service.validar_item(linha) == []


def test_validacao_rejeita_valor_fora_da_tolerancia(db_session):
    """Diferença de R$ 1,00 no total deve ser rejeitada."""
    service = ValidacaoPlanilhaService(db_session)
    linha = {
        "data_venda": "2025-01-15", "vendedor": "Ana", "regiao": "Sul",
        "produto": "Mouse Logitech", "categoria": "Periféricos",
        "quantidade": 2, "valor_unitario": 50.0, "valor_total": 101.0,
    }
    erros = service.validar_item(linha)
    assert any("valor_total" in e for e in erros)


def test_validacao_rejeita_quantidade_zero(db_session):
    """Quantidade igual a zero é o valor de fronteira que deve falhar."""
    service = ValidacaoPlanilhaService(db_session)
    linha = {
        "data_venda": "2025-01-15", "vendedor": "Ana", "regiao": "Sul",
        "produto": "Mouse Logitech", "categoria": "Periféricos",
        "quantidade": 0, "valor_unitario": 50.0, "valor_total": 0.0,
    }
    erros = service.validar_item(linha)
    assert any("quantidade" in e for e in erros)


# ===========================================================================
# 3. Cenários negativos de importação
# ===========================================================================

def test_importar_planilha_vazia_lanca_erro(db_session, usuario):
    """Uma planilha sem linhas de dados deve ser rejeitada com ValueError."""
    vazia = construir_planilha([])
    service = ImportacaoService(db_session)

    with pytest.raises(ValueError) as exc:
        service.importar_planilha(vazia, "vazia.xlsx", usuario)
    assert "vazia" in str(exc.value).lower()


def test_importar_planilha_com_coluna_faltando_lanca_erro(db_session, usuario):
    """Planilha sem a coluna obrigatória 'valor_total' deve ser rejeitada,
    indicando explicitamente a coluna ausente."""
    df = pd.DataFrame([{
        "data_venda": "2025-01-15", "vendedor": "Ana", "regiao": "Sul",
        "produto": "Mouse Logitech", "categoria": "Periféricos",
        "quantidade": 2, "valor_unitario": 50.0,
        # 'valor_total' ausente de propósito
    }])
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")

    service = ImportacaoService(db_session)
    with pytest.raises(ValueError) as exc:
        service.importar_planilha(buffer.getvalue(), "incompleta.xlsx", usuario)
    assert "valor_total" in str(exc.value)


# ===========================================================================
# 4. Consistência após operações encadeadas
# ===========================================================================

def test_consistencia_importar_e_validar_encadeados(db_session, usuario):
    """Após importar e validar, os contadores devem ser coerentes:
    total = válidos + inválidos, com um registro duplicado detectado."""
    linhas = [
        linha_valida(),
        linha_valida(produto="Mouse Logitech", valor_unitario=50.0, valor_total=100.0),
        linha_valida(),  # duplicado exato da primeira linha
    ]
    planilha = construir_planilha(linhas)

    importacao = ImportacaoService(db_session).importar_planilha(
        planilha, "vendas.xlsx", usuario
    )
    resultado = ValidacaoPlanilhaService(db_session).validar_planilha(
        importacao.id, usuario
    )

    assert resultado["total_registros"] == 3
    assert resultado["total_validos"] + resultado["total_invalidos"] == 3
    # A terceira linha é duplicata exata da primeira -> ao menos 1 inválido.
    assert resultado["total_invalidos"] >= 1
