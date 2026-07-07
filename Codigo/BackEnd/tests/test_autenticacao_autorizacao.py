"""Testes de autenticação e autorização (JWT + perfis de acesso).

Estes testes cobrem os fluxos de segurança do sistema, atendendo à
recomendação de ampliar a cobertura para cenários de autenticação,
autorização e casos de exceção, além dos caminhos de sucesso.

Cobrem:
  - autenticação com senha correta, senha incorreta e usuário inexistente;
  - bloqueio de usuário desativado;
  - emissão e decodificação de token JWT (incluindo token inválido e expirado);
  - resolução do usuário atual a partir do token (get_current_user);
  - autorização por perfil (require_roles), com acesso concedido e negado.
"""

from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from jose import jwt

from app.core import auth
from app.core.config import settings
from app.db import models
from app.services.usuario_service import UsuarioService, hash_password


# ---------------------------------------------------------------------------
# Fixtures locais
# ---------------------------------------------------------------------------

@pytest.fixture()
def usuario_com_senha(db_session):
    """Cria um gestor com senha conhecida ('senha123')."""
    usuario = models.Usuario(
        nome="Gestor Teste",
        email="gestor.teste@dashvendas.com",
        senha_hash=hash_password("senha123"),
        tipo_usuario="gestor",
        ativo=True,
    )
    db_session.add(usuario)
    db_session.commit()
    return usuario


# ---------------------------------------------------------------------------
# Autenticação (UsuarioService.autenticar)
# ---------------------------------------------------------------------------

def test_autenticar_com_credenciais_corretas(db_session, usuario_com_senha):
    resultado = UsuarioService(db_session).autenticar(
        "gestor.teste@dashvendas.com", "senha123"
    )
    assert resultado is not None
    assert resultado.email == "gestor.teste@dashvendas.com"


def test_autenticar_com_senha_incorreta(db_session, usuario_com_senha):
    resultado = UsuarioService(db_session).autenticar(
        "gestor.teste@dashvendas.com", "senha_errada"
    )
    assert resultado is None


def test_autenticar_usuario_inexistente(db_session):
    resultado = UsuarioService(db_session).autenticar(
        "naoexiste@dashvendas.com", "qualquer"
    )
    assert resultado is None


def test_autenticar_usuario_desativado(db_session, usuario_com_senha):
    # Desativa o usuário; mesmo com a senha correta, não deve autenticar.
    usuario_com_senha.ativo = False
    db_session.commit()

    resultado = UsuarioService(db_session).autenticar(
        "gestor.teste@dashvendas.com", "senha123"
    )
    assert resultado is None


# ---------------------------------------------------------------------------
# Token JWT (create_access_token / decode_token)
# ---------------------------------------------------------------------------

def test_token_valido_ida_e_volta():
    token = auth.create_access_token({"sub": "42"})
    payload = auth.decode_token(token)
    assert payload["sub"] == "42"


def test_token_invalido_gera_401():
    with pytest.raises(HTTPException) as exc:
        auth.decode_token("token.completamente.invalido")
    assert exc.value.status_code == 401


def test_token_expirado_gera_401():
    # Gera manualmente um token já expirado.
    expirado = datetime.now(timezone.utc) - timedelta(minutes=5)
    token = jwt.encode(
        {"sub": "1", "exp": expirado},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    with pytest.raises(HTTPException) as exc:
        auth.decode_token(token)
    assert exc.value.status_code == 401


# ---------------------------------------------------------------------------
# Resolução do usuário atual (get_current_user)
# ---------------------------------------------------------------------------

def test_get_current_user_retorna_usuario(db_session, usuario_com_senha):
    token = auth.create_access_token({"sub": str(usuario_com_senha.id)})
    atual = auth.get_current_user(token=token, db=db_session)
    assert atual.id == usuario_com_senha.id


def test_get_current_user_usuario_inexistente(db_session):
    token = auth.create_access_token({"sub": "9999"})
    with pytest.raises(HTTPException) as exc:
        auth.get_current_user(token=token, db=db_session)
    assert exc.value.status_code == 401


def test_get_current_user_desativado_gera_403(db_session, usuario_com_senha):
    usuario_com_senha.ativo = False
    db_session.commit()
    token = auth.create_access_token({"sub": str(usuario_com_senha.id)})
    with pytest.raises(HTTPException) as exc:
        auth.get_current_user(token=token, db=db_session)
    assert exc.value.status_code == 403


# ---------------------------------------------------------------------------
# Autorização por perfil (require_roles)
# ---------------------------------------------------------------------------

def test_require_roles_concede_acesso_ao_perfil_correto(usuario_com_senha):
    verificador = auth.require_roles("gestor", "administrador")
    # O gestor está entre os perfis permitidos: deve retornar o próprio usuário.
    resultado = verificador(current_user=usuario_com_senha)
    assert resultado is usuario_com_senha


def test_require_roles_nega_acesso_a_perfil_nao_autorizado(usuario_com_senha):
    verificador = auth.require_roles("administrador")  # gestor não incluído
    with pytest.raises(HTTPException) as exc:
        verificador(current_user=usuario_com_senha)
    assert exc.value.status_code == 403
