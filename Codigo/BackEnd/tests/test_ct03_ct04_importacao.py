"""Casos de Teste de Aceitação CT03 e CT04 — Importação de Planilhas.

Referência: Seção 6.1 da Documentação de Projeto (Tabelas 9 e 10).

CT03 - Importar Planilha para Análise (Arquivo Válido):
    valida que o sistema importa arquivos .xlsx com estrutura válida,
    registra a importação e a deixa disponível para as etapas seguintes.

CT04 - Importar Planilha para Análise (Formato Inválido):
    valida que o sistema rejeita arquivos em formatos não permitidos,
    não registrando dados de itens no banco.

Sistemas envolvidos: ImportacaoService, ImportacaoRepository, LogRepository.
"""

import pytest

from app.repositories.repositories import ImportacaoRepository, LogRepository
from app.services.importacao_service import ImportacaoService
from tests._helpers import construir_planilha, linha_valida


class TestCT03ImportarArquivoValido:
    """CT03 - Importação de arquivo válido."""

    def test_importa_planilha_valida_registra_importacao(self, db_session, usuario):
        # Pré-condição: arquivo .xlsx com as colunas obrigatórias.
        conteudo = construir_planilha([
            linha_valida(),
            linha_valida(produto="Mouse Logitech", quantidade=5,
                         valor_unitario=50.0, valor_total=250.0),
        ])

        # Ação: o usuário importa o arquivo válido.
        importacao = ImportacaoService(db_session).importar_planilha(
            conteudo, "vendas_janeiro.xlsx", usuario
        )

        # Resultado esperado: importação registrada e itens persistidos.
        assert importacao.id is not None
        assert importacao.status == "importada"
        assert importacao.nome_arquivo == "vendas_janeiro.xlsx"

        itens = ImportacaoRepository(db_session).listar_itens(importacao.id)
        assert len(itens) == 2
        assert all(item.status == "pendente_validacao" for item in itens)

    def test_importacao_registra_log_auditoria(self, db_session, usuario):
        # CT03 — pós-condição: a operação é registrada em log (LogRepository).
        conteudo = construir_planilha([linha_valida()])
        ImportacaoService(db_session).importar_planilha(conteudo, "vendas.xlsx", usuario)

        logs = LogRepository(db_session).listar(tipo_operacao="importacao_planilha")
        assert len(logs) == 1
        assert "vendas.xlsx" in logs[0].resumo

    def test_planilha_sem_colunas_obrigatorias_eh_rejeitada(self, db_session, usuario):
        # Estrutura inválida (faltam colunas) deve gerar erro de validação.
        import io
        import pandas as pd

        df = pd.DataFrame([{"produto": "X", "valor": 10}])
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False, engine="openpyxl")

        with pytest.raises(ValueError, match="Colunas obrigatórias ausentes"):
            ImportacaoService(db_session).importar_planilha(
                buffer.getvalue(), "incompleta.xlsx", usuario
            )


class TestCT04ImportarFormatoInvalido:
    """CT04 - Rejeição de formato inválido."""

    def test_arquivo_nao_excel_nao_eh_lido(self, db_session, usuario):
        # Pré-condição: arquivo em formato incompatível (.txt/.pdf).
        # O serviço de importação lê via openpyxl; bytes de texto puro
        # não constituem um Excel válido e devem gerar erro de leitura.
        conteudo_txt = b"isto e um arquivo de texto, nao um excel"

        with pytest.raises(ValueError):
            ImportacaoService(db_session).importar_planilha(
                conteudo_txt, "documento.txt", usuario
            )

    def test_formato_invalido_nao_persiste_itens(self, db_session, usuario):
        # Pós-condição (CT04): nenhuma informação de item é registrada.
        conteudo_txt = b"%PDF-1.4 conteudo binario qualquer"

        with pytest.raises(ValueError):
            ImportacaoService(db_session).importar_planilha(
                conteudo_txt, "relatorio.pdf", usuario
            )

        # Nenhum item de importação deve ter sido criado.
        from app.db import models
        total_itens = db_session.query(models.ImportacaoItem).count()
        assert total_itens == 0

    def test_registrar_erro_marca_importacao_com_status_erro(self, db_session, usuario):
        # O controller, ao detectar extensão inválida, chama registrar_erro:
        # garante rastreabilidade da tentativa sem processar dados.
        service = ImportacaoService(db_session)
        service.registrar_erro("planilha.pdf", usuario, "Extensão inválida")

        from app.db import models
        importacao = db_session.query(models.Importacao).first()
        assert importacao is not None
        assert importacao.status == "erro"
        assert db_session.query(models.ImportacaoItem).count() == 0
