"""UsuarioController — UC14 (Gerenciar usuários e permissões)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import require_roles
from app.db.database import get_db
from app.dtos.schemas import UsuarioCreateDTO, UsuarioUpdateDTO
from app.services.usuario_service import UsuarioService

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


def _serializar(usuario):
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "role": usuario.tipo_usuario,
        "ativo": usuario.ativo,
    }


@router.get("")
def listar_usuarios(
    current_user=Depends(require_roles("administrador")),
    db: Session = Depends(get_db),
):
    return [_serializar(u) for u in UsuarioService(db).listar()]


@router.post("")
def criar_usuario(
    payload: UsuarioCreateDTO,
    current_user=Depends(require_roles("administrador")),
    db: Session = Depends(get_db),
):
    service = UsuarioService(db)

    if service.obter_por_email(payload.email):
        raise HTTPException(status_code=400, detail="Já existe um usuário com este e-mail")

    usuario = service.criar_usuario(
        nome=payload.nome,
        email=payload.email,
        senha=payload.senha,
        tipo_usuario=payload.tipo_usuario,
        admin=current_user,
    )
    return _serializar(usuario)


@router.put("/{usuario_id}")
def ajustar_permissoes(
    usuario_id: int,
    payload: UsuarioUpdateDTO,
    current_user=Depends(require_roles("administrador")),
    db: Session = Depends(get_db),
):
    """CO15 — ajustarPermissoes(usuario, novasPermissoes)."""

    usuario = UsuarioService(db).ajustar_permissoes(
        usuario_id,
        admin=current_user,
        nome=payload.nome,
        email=payload.email,
        tipo_usuario=payload.tipo_usuario,
        senha=payload.senha,
        ativo=payload.ativo,
    )
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return _serializar(usuario)


@router.delete("/{usuario_id}")
def remover_usuario(
    usuario_id: int,
    current_user=Depends(require_roles("administrador")),
    db: Session = Depends(get_db),
):
    if usuario_id == current_user.id:
        raise HTTPException(status_code=400, detail="Não é possível remover o próprio usuário")

    if not UsuarioService(db).remover_usuario(usuario_id, admin=current_user):
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"message": "Usuário removido com sucesso"}
