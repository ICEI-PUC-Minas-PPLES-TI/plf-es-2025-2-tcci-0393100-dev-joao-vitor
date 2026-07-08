"""Testes unitários — usuários/permissões (UC14/CO15) e relatórios/agendamentos."""

from app.db import models
from app.services.agendamento_service import AgendamentoService
from app.services.relatorio_service import RelatorioService
from app.services.usuario_service import UsuarioService, hash_password, verify_password


# ---------------------------------------------------------------------------
# Usuários e permissões (UC14 / CO15)
# ---------------------------------------------------------------------------

def test_hash_de_senha_e_verificacao():
    h = hash_password("123456")
    assert h != "123456"
    assert verify_password("123456", h) is True
    assert verify_password("errada", h) is False


def test_autenticacao_com_credenciais_validas(db_session):
    service = UsuarioService(db_session)
    admin = db_session.query(models.Usuario).first()

    novo = service.criar_usuario(
        "Gestor X", "gestorx@dashvendas.com", "senha123", "gestor", admin=admin
    )

    autenticado = service.autenticar("gestorx@dashvendas.com", "senha123")
    assert autenticado is not None
    assert autenticado.id == novo.id


def test_autenticacao_falha_para_usuario_inativo(db_session):
    service = UsuarioService(db_session)
    admin = db_session.query(models.Usuario).first()

    service.criar_usuario("Inativo", "inativo@dashvendas.com", "s", "vendedor", admin=admin)
    usuario = service.obter_por_email("inativo@dashvendas.com")
    service.ajustar_permissoes(usuario.id, admin=admin, ativo=False)

    assert service.autenticar("inativo@dashvendas.com", "s") is None


def test_ajuste_de_permissoes_gera_log(db_session):
    service = UsuarioService(db_session)
    admin = db_session.query(models.Usuario).first()

    usuario = service.criar_usuario(
        "Maria", "maria2@dashvendas.com", "s", "vendedor", admin=admin
    )
    service.ajustar_permissoes(usuario.id, admin=admin, tipo_usuario="gestor")

    from app.repositories.repositories import LogRepository
    logs = LogRepository(db_session).listar(tipo_operacao="alteracao_permissoes")
    # Criação + alteração de perfil = 2 logs
    assert len(logs) >= 2


def test_remocao_de_usuario(db_session):
    service = UsuarioService(db_session)
    admin = db_session.query(models.Usuario).first()

    usuario = service.criar_usuario(
        "Temp", "temp@dashvendas.com", "s", "vendedor", admin=admin
    )
    assert service.remover_usuario(usuario.id, admin=admin) is True
    assert service.obter_por_id(usuario.id) is None


# ---------------------------------------------------------------------------
# Relatórios (UC06) e Agendamentos (UC07 / UC15)
# ---------------------------------------------------------------------------

def test_gerar_relatorio_consolidado(db_session, usuario):
    relatorio, conteudo = RelatorioService(db_session).gerar_relatorio(usuario_id=usuario.id)

    assert relatorio.id is not None
    assert relatorio.tipo == "consolidado"
    assert "Relatório Consolidado" in conteudo

    from app.repositories.repositories import LogRepository
    logs = LogRepository(db_session).listar(tipo_operacao="geracao_relatorio")
    assert len(logs) == 1


def test_registrar_e_listar_agendamento(db_session, usuario):
    service = AgendamentoService(db_session)
    service.registrar_agendamento(
        usuario_id=usuario.id,
        periodicidade="mensal",
        destinatarios="gestor@dashvendas.com",
        filtros=None,
    )

    agendamentos = service.listar_agendamentos()
    assert len(agendamentos) == 1
    assert agendamentos[0].periodicidade == "mensal"
    assert agendamentos[0].ativo is True


def test_executar_envio_agendado_gera_relatorios(db_session, usuario):
    service = AgendamentoService(db_session)
    service.registrar_agendamento(
        usuario_id=usuario.id,
        periodicidade="mensal",
        destinatarios="gestor@dashvendas.com",
    )

    envios = service.executar_envio_agendado()

    assert len(envios) == 1
    assert envios[0]["relatorio_id"] is not None

    from app.repositories.repositories import LogRepository
    logs = LogRepository(db_session).listar(tipo_operacao="envio_relatorio_agendado")
    assert len(logs) == 1


def test_agendamento_inativo_nao_e_executado(db_session, usuario):
    service = AgendamentoService(db_session)
    agendamento = service.registrar_agendamento(
        usuario_id=usuario.id,
        periodicidade="mensal",
        destinatarios="gestor@dashvendas.com",
    )
    service.alterar_status(agendamento.id, ativo=False)

    envios = service.executar_envio_agendado()
    assert len(envios) == 0
