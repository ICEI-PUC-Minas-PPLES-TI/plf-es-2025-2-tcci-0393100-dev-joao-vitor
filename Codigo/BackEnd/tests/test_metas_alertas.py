"""Testes unitários — metas (UC03/UC04) e alertas (UC05)."""

from datetime import date

from app.db import models
from app.services.alerta_service import AlertaService
from app.services.meta_service import MetaService


def _criar_venda(db, valor=1000.0, regiao="Sudeste", categoria="Informática"):
    db.add(models.Venda(
        data_venda=date(2026, 4, 15),
        quantidade=1,
        valor_total=valor,
        vendedor_nome="João",
        regiao_nome=regiao,
        produto_nome="Notebook Dell",
        categoria_nome=categoria,
    ))
    db.commit()


# ---------------------------------------------------------------------------
# Metas (UC03 / UC04)
# ---------------------------------------------------------------------------

def test_meta_atingida_quando_realizado_supera_meta(db_session, usuario):
    _criar_venda(db_session, 1500.0)

    service = MetaService(db_session)
    service.registrar_meta("2026-04-01", "2026-04-30", None, None, 1000.0, usuario_id=usuario.id)

    metas = service.consultar_atingimento_metas()
    assert metas[0]["status"] == "atingida"
    assert metas[0]["percentual_atingimento"] == 150.0


def test_meta_em_risco_entre_70_e_100(db_session, usuario):
    _criar_venda(db_session, 800.0)

    service = MetaService(db_session)
    service.registrar_meta("2026-04-01", "2026-04-30", None, None, 1000.0, usuario_id=usuario.id)

    metas = service.consultar_atingimento_metas()
    assert metas[0]["status"] == "em_risco"


def test_meta_nao_atingida_abaixo_de_70(db_session, usuario):
    _criar_venda(db_session, 500.0)

    service = MetaService(db_session)
    service.registrar_meta("2026-04-01", "2026-04-30", None, None, 1000.0, usuario_id=usuario.id)

    metas = service.consultar_atingimento_metas()
    assert metas[0]["status"] == "nao_atingida"


def test_meta_filtra_por_regiao(db_session, usuario):
    _criar_venda(db_session, 1000.0, regiao="Sudeste")
    _criar_venda(db_session, 1000.0, regiao="Sul")

    service = MetaService(db_session)
    service.registrar_meta("2026-04-01", "2026-04-30", "Sudeste", None, 1000.0, usuario_id=usuario.id)

    metas = service.consultar_atingimento_metas()
    # Apenas a venda do Sudeste conta para a meta regional
    assert metas[0]["total_realizado"] == 1000.0


def test_excluir_meta(db_session, usuario):
    service = MetaService(db_session)
    meta = service.registrar_meta("2026-04-01", "2026-04-30", None, None, 1000.0, usuario_id=usuario.id)

    assert service.excluir_meta(meta.id) is True
    assert service.consultar_atingimento_metas() == []


def test_calcular_status_limites_exatos():
    assert MetaService.calcular_status_atingimento(100) == "atingida"
    assert MetaService.calcular_status_atingimento(70) == "em_risco"
    assert MetaService.calcular_status_atingimento(69.99) == "nao_atingida"


# ---------------------------------------------------------------------------
# Alertas (UC05)
# ---------------------------------------------------------------------------

def test_alerta_critico_para_meta_nao_atingida(db_session, usuario):
    _criar_venda(db_session, 100.0)

    MetaService(db_session).registrar_meta(
        "2026-04-01", "2026-04-30", None, None, 1000.0, usuario_id=usuario.id
    )

    alertas = AlertaService(db_session).consultar_alertas()
    assert len(alertas) == 1
    assert alertas[0].nivel_criticidade == "alto"


def test_alerta_medio_para_meta_em_risco(db_session, usuario):
    _criar_venda(db_session, 800.0)

    MetaService(db_session).registrar_meta(
        "2026-04-01", "2026-04-30", None, None, 1000.0, usuario_id=usuario.id
    )

    alertas = AlertaService(db_session).consultar_alertas()
    assert len(alertas) == 1
    assert alertas[0].nivel_criticidade == "medio"


def test_meta_atingida_nao_gera_alerta(db_session, usuario):
    _criar_venda(db_session, 2000.0)

    MetaService(db_session).registrar_meta(
        "2026-04-01", "2026-04-30", None, None, 1000.0, usuario_id=usuario.id
    )

    alertas = AlertaService(db_session).consultar_alertas()
    assert len(alertas) == 0


def test_alertas_nao_sao_duplicados(db_session, usuario):
    _criar_venda(db_session, 100.0)

    MetaService(db_session).registrar_meta(
        "2026-04-01", "2026-04-30", None, None, 1000.0, usuario_id=usuario.id
    )

    service = AlertaService(db_session)
    service.consultar_alertas()
    alertas = service.consultar_alertas()  # segunda chamada não duplica

    assert len(alertas) == 1


def test_marcar_alerta_como_lido(db_session, usuario):
    _criar_venda(db_session, 100.0)
    MetaService(db_session).registrar_meta(
        "2026-04-01", "2026-04-30", None, None, 1000.0, usuario_id=usuario.id
    )

    service = AlertaService(db_session)
    alerta = service.consultar_alertas()[0]
    assert alerta.lido is False

    atualizado = service.marcar_como_lido(alerta.id)
    assert atualizado.lido is True
