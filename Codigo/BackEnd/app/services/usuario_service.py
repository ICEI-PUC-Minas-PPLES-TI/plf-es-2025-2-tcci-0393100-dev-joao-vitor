"""UsuarioService — UC14 (Gerenciar usuários e permissões).

Conforme o contrato CO15, alterações de permissões são registradas
internamente em log de auditoria (US13).
"""

from typing import Optional

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.db import models
from app.repositories.repositories import LogRepository, UsuarioRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


class UsuarioService:
    def __init__(self, db: Session):
        self.db = db
        self.usuario_repository = UsuarioRepository(db)
        self.log_repository = LogRepository(db)

    def autenticar(self, email: str, senha: str) -> Optional[models.Usuario]:
        usuario = self.usuario_repository.obter_por_email(email)
        if not usuario or not verify_password(senha, usuario.senha_hash):
            return None
        if usuario.ativo is False:
            return None
        return usuario

    def obter_por_id(self, usuario_id: int) -> Optional[models.Usuario]:
        return self.usuario_repository.obter_por_id(usuario_id)

    def obter_por_email(self, email: str) -> Optional[models.Usuario]:
        return self.usuario_repository.obter_por_email(email)

    def listar(self) -> list[models.Usuario]:
        return self.usuario_repository.listar()

    def criar_usuario(self, nome: str, email: str, senha: str, tipo_usuario: str, admin) -> models.Usuario:
        usuario = models.Usuario(
            nome=nome,
            email=email,
            senha_hash=hash_password(senha),
            tipo_usuario=tipo_usuario,
        )
        usuario = self.usuario_repository.salvar(usuario)

        self.log_repository.registrar(
            tipo_operacao="alteracao_permissoes",
            resumo=f"Usuário '{usuario.email}' criado com perfil '{tipo_usuario}'.",
            usuario_id=admin.id,
        )

        return usuario

    def ajustar_permissoes(
        self,
        usuario_id: int,
        admin,
        nome: Optional[str] = None,
        email: Optional[str] = None,
        tipo_usuario: Optional[str] = None,
        senha: Optional[str] = None,
        ativo: Optional[bool] = None,
    ) -> Optional[models.Usuario]:
        """CO15 — ajustarPermissoes(usuario, novasPermissoes)."""

        usuario = self.usuario_repository.obter_por_id(usuario_id)
        if not usuario:
            return None

        alteracoes = []

        if nome is not None and nome != usuario.nome:
            usuario.nome = nome
            alteracoes.append("nome")
        if email is not None and email != usuario.email:
            usuario.email = email
            alteracoes.append("email")
        if tipo_usuario is not None and tipo_usuario != usuario.tipo_usuario:
            alteracoes.append(f"perfil {usuario.tipo_usuario} -> {tipo_usuario}")
            usuario.tipo_usuario = tipo_usuario
        if senha:
            usuario.senha_hash = hash_password(senha)
            alteracoes.append("senha")
        if ativo is not None and ativo != usuario.ativo:
            usuario.ativo = ativo
            alteracoes.append("ativado" if ativo else "desativado")

        usuario = self.usuario_repository.salvar(usuario)

        if alteracoes:
            self.log_repository.registrar(
                tipo_operacao="alteracao_permissoes",
                resumo=f"Usuário '{usuario.email}' atualizado: {', '.join(alteracoes)}.",
                usuario_id=admin.id,
            )

        return usuario

    def remover_usuario(self, usuario_id: int, admin) -> bool:
        usuario = self.usuario_repository.obter_por_id(usuario_id)
        if not usuario:
            return False

        email = usuario.email
        self.usuario_repository.remover(usuario)

        self.log_repository.registrar(
            tipo_operacao="alteracao_permissoes",
            resumo=f"Usuário '{email}' removido do sistema.",
            usuario_id=admin.id,
        )

        return True
