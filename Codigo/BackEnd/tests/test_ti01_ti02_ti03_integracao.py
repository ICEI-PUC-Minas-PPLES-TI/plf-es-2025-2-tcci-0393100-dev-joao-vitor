"""Casos de Teste de Integração TI01, TI02 e TI03.

Referência: Seção 6.2 da Documentação de Projeto (Tabelas 11, 12 e 13).

TI01 - Integração entre Importação e Validação:
    após a importação, a validação é acionada e registra o status da
    operação, deixando o arquivo disponível para consulta.
    Sistemas: ImportacaoService, ValidacaoPlanilhaService, LogRepository.

TI02 - Integração entre Cruzamento de Produtos e Cálculo de KPIs:
    os produtos corretamente cruzados consolidam vendas que são, então,
    utilizadas no cálculo dos KPIs.
    Sistemas: CruzamentoProdutoService, KPIService, VendaRepository.

TI03 - Integração entre IA e Cálculo de KPIs:
    o serviço de IA recebe os dados de KPIs (via gateway/Adapter) e
    produz uma análise coerente com esses dados.
    Sistemas: IAService, IAGateway, KPIService.
"""

from app.integrations.ia_gateway import IAGateway
from app.repositories.repositories import ImportacaoRepository, LogRepository
from app.services.cruzamento_produto_service import CruzamentoProdutoService
from app.services.ia_service import IAService
from app.services.importacao_service import ImportacaoService
from app.services.kpi_service import KPIService
from app.services.validacao_planilha_service import ValidacaoPlanilhaService
from tests._helpers import construir_planilha, linha_valida


def _importar_validar_cruzar(db_session, usuario, linhas):
    """Fluxo completo de importação -> validação -> cruzamento."""

    conteudo = construir_planilha(linhas)
    importacao = ImportacaoService(db_session).importar_planilha(
        conteudo, "vendas.xlsx", usuario
    )
    validacao = ValidacaoPlanilhaService(db_session).validar_planilha(
        importacao.id, usuario
    )
    cruzamento = CruzamentoProdutoService(db_session).cruzar_produtos(
        importacao.id, usuario
    )
    return importacao, validacao, cruzamento


class TestTI01ImportacaoValidacao:
    """TI01 - Importação aciona validação e registra status."""

    def test_validacao_apos_importacao_registra_status_e_log(self, db_session, usuario):
        conteudo = construir_planilha([
            linha_valida(),
            linha_valida(produto="Mouse Logitech", quantidade=5,
                         valor_unitario=50.0, valor_total=250.0),
        ])

        importacao = ImportacaoService(db_session).importar_planilha(
            conteudo, "vendas.xlsx", usuario
        )
        assert importacao.status == "importada"

        resultado = ValidacaoPlanilhaService(db_session).validar_planilha(
            importacao.id, usuario
        )

        # Resultado esperado: arquivo e resultados de validação registrados.
        assert resultado["total_registros"] == 2
        assert resultado["total_validos"] == 2
        assert resultado["total_invalidos"] == 0
        assert importacao.status == "validada"

        # O fluxo registra logs de importação e de validação.
        logs = LogRepository(db_session).listar()
        tipos = {log.tipo_operacao for log in logs}
        assert "importacao_planilha" in tipos
        assert "validacao_planilha" in tipos

    def test_validacao_identifica_registros_invalidos(self, db_session, usuario):
        conteudo = construir_planilha([
            linha_valida(),
            # valor_total incompatível (qtd * unitário != total)
            linha_valida(quantidade=2, valor_unitario=1000.0, valor_total=999.0),
            # quantidade ausente
            linha_valida(quantidade=None),
        ])

        importacao = ImportacaoService(db_session).importar_planilha(
            conteudo, "vendas.xlsx", usuario
        )
        resultado = ValidacaoPlanilhaService(db_session).validar_planilha(
            importacao.id, usuario
        )

        assert resultado["total_validos"] == 1
        assert resultado["total_invalidos"] == 2
        assert importacao.status == "validada_com_alertas"


class TestTI02CruzamentoKpis:
    """TI02 - Produtos cruzados alimentam o cálculo de KPIs."""

    def test_cruzamento_consolida_vendas_para_kpis(self, db_session, usuario):
        _, _, cruzamento = _importar_validar_cruzar(db_session, usuario, [
            linha_valida(produto="Notebook Dell", quantidade=2,
                         valor_unitario=1000.0, valor_total=2000.0),
            linha_valida(produto="Mouse Logitech", regiao="Sul", quantidade=5,
                         valor_unitario=50.0, valor_total=250.0),
        ])

        # Produtos do catálogo devem ter sido encontrados no cruzamento.
        assert cruzamento["encontrados"] == 2
        assert cruzamento["nao_encontrados"] == 0

        # Após o cruzamento, os KPIs refletem as vendas consolidadas.
        kpis = KPIService(db_session).calcular_kpis()
        assert kpis["resumo"]["total_vendas"] == 2250.0
        assert kpis["resumo"]["total_pedidos"] == 2

    def test_kpis_por_regiao_apos_cruzamento(self, db_session, usuario):
        _importar_validar_cruzar(db_session, usuario, [
            linha_valida(produto="Notebook Dell", regiao="Sudeste",
                         quantidade=2, valor_unitario=1000.0, valor_total=2000.0),
            linha_valida(produto="Monitor LG", regiao="Sul",
                         quantidade=1, valor_unitario=900.0, valor_total=900.0),
        ])

        kpis = KPIService(db_session).calcular_kpis(regiao="Sul")
        assert kpis["resumo"]["total_vendas"] == 900.0
        assert kpis["resumo"]["total_pedidos"] == 1


class _FakeGateway(IAGateway):
    """Adaptador de IA falso que ecoa os KPIs recebidos (testa TI03).

    Simula um provedor externo, permitindo verificar que o IAService
    repassa corretamente o contexto de KPIs ao gateway (padrão Adapter)
    sem depender de rede.
    """

    nome = "fake_externo"

    def __init__(self):
        self.ultimo_contexto = None

    def gerar_resposta(self, prompt, contexto):
        self.ultimo_contexto = contexto
        total = contexto["kpis"]["resumo"]["total_vendas"]
        return f"Analise externa: total de vendas {total}."


class TestTI03IaKpis:
    """TI03 - A IA recebe os KPIs e gera análise coerente."""

    def test_ia_recebe_kpis_no_contexto(self, db_session, usuario):
        _importar_validar_cruzar(db_session, usuario, [
            linha_valida(produto="Notebook Dell", quantidade=2,
                         valor_unitario=1000.0, valor_total=2000.0),
        ])

        gateway = _FakeGateway()
        resultado = IAService(db_session, gateway=gateway).gerar_analise()

        # O gateway (Adapter) deve ter recebido os KPIs como contexto.
        assert gateway.ultimo_contexto is not None
        assert gateway.ultimo_contexto["kpis"]["resumo"]["total_vendas"] == 2000.0

        # A resposta retornada provém do provedor e cita o dado correto.
        assert resultado["provedor"] == "fake_externo"
        assert "2000" in resultado["resposta"]

    def test_fallback_local_quando_gateway_retorna_none(self, db_session, usuario):
        from app.integrations.ia_gateway import LocalIAGateway

        _importar_validar_cruzar(db_session, usuario, [
            linha_valida(produto="Notebook Dell", quantidade=2,
                         valor_unitario=1000.0, valor_total=2000.0),
        ])

        # LocalIAGateway retorna None -> IAService compõe resposta local.
        resultado = IAService(db_session, gateway=LocalIAGateway()).gerar_analise()
        assert resultado["provedor"] == "local"
        assert resultado["dados"]["total_vendas"] == 2000.0
        assert "vendas" in resultado["resposta"].lower()

    def test_consulta_linguagem_natural_usa_kpis(self, db_session, usuario):
        from app.integrations.ia_gateway import LocalIAGateway

        _importar_validar_cruzar(db_session, usuario, [
            linha_valida(produto="Notebook Dell", quantidade=2,
                         valor_unitario=1000.0, valor_total=2000.0),
        ])

        resposta = IAService(db_session, gateway=LocalIAGateway()).consultar_ia(
            "Qual o total de vendas?"
        )
        assert "2.000" in resposta["resposta"] or "2000" in resposta["resposta"]
