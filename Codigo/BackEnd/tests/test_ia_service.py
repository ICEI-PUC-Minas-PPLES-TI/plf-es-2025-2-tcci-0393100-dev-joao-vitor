"""Testes unitários — assistente de IA (UC12/UC13) com adaptador local."""

from datetime import date

from app.db import models
from app.services.ia_service import IAService
from app.services.meta_service import MetaService


def _povoar(db):
    vendas = [
        ("Sudeste", "Informática", "Carlos", 5000.0),
        ("Sul", "Periféricos", "Maria", 1000.0),
        ("Nordeste", "Informática", "Carlos", 2000.0),
    ]
    for regiao, categoria, vendedor, valor in vendas:
        db.add(models.Venda(
            data_venda=date(2026, 4, 1),
            quantidade=1,
            valor_total=valor,
            vendedor_nome=vendedor,
            regiao_nome=regiao,
            produto_nome="Produto",
            categoria_nome=categoria,
        ))

    # As regiões de referência já são criadas pela fixture (conftest);
    # aqui apenas as vendas são necessárias, pois os KPIs usam o campo
    # textual 'regiao_nome' das próprias vendas.
    db.commit()


# ---------------------------------------------------------------------------
# UC12 - Análise interpretativa
# ---------------------------------------------------------------------------

def test_analise_interpretativa_menciona_lider(db_session):
    _povoar(db_session)

    resultado = IAService(db_session).gerar_analise()

    assert resultado["provedor"] == "local"
    # A região líder (Sudeste, 5000) deve ser destacada
    assert "Sudeste" in resultado["resposta"]
    assert resultado["dados"]["total_vendas"] == 8000.0


def test_analise_sem_vendas_orienta_importacao(db_session):
    resultado = IAService(db_session).gerar_analise()
    assert "Importe uma planilha" in resultado["resposta"]


def test_analise_destaca_metas_em_risco(db_session, usuario):
    _povoar(db_session)
    MetaService(db_session).registrar_meta(
        "2026-04-01", "2026-04-30", None, None, 100000.0, usuario_id=usuario.id
    )

    resultado = IAService(db_session).gerar_analise()
    assert "risco" in resultado["resposta"].lower()


# ---------------------------------------------------------------------------
# UC13 - Pergunta em linguagem natural
# ---------------------------------------------------------------------------

def test_pergunta_extrai_regiao_da_frase(db_session):
    _povoar(db_session)

    resultado = IAService(db_session).consultar_ia(
        "Qual o total de vendas na região Sul?"
    )

    assert resultado["contexto"]["regiao"] == "Sul"
    assert "1.000,00" in resultado["resposta"]


def test_pergunta_extrai_categoria_da_frase(db_session):
    _povoar(db_session)

    resultado = IAService(db_session).consultar_ia(
        "Como estão as vendas de Informática?"
    )

    assert resultado["contexto"]["categoria"] == "Informática"


def test_pergunta_ranking_de_regioes(db_session):
    _povoar(db_session)

    resultado = IAService(db_session).consultar_ia("Qual a melhor região em vendas?")

    # Sudeste deve aparecer em primeiro no ranking
    assert "Sudeste" in resultado["resposta"]
    assert resultado["contexto"]["tipo"] == "ranking"


def test_pergunta_sobre_metas(db_session, usuario):
    _povoar(db_session)
    MetaService(db_session).registrar_meta(
        "2026-04-01", "2026-04-30", None, None, 5000.0, usuario_id=usuario.id
    )

    resultado = IAService(db_session).consultar_ia(
        "Qual o atingimento das metas?"
    )

    assert resultado["contexto"]["tipo"] == "metas"


def test_pergunta_resumo_geral(db_session):
    _povoar(db_session)

    resultado = IAService(db_session).consultar_ia("Me dê um resumo das vendas")

    assert resultado["contexto"]["tipo"] == "resumo"
    assert "8.000,00" in resultado["resposta"]
