

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import require_roles
from app.db.database import get_db
from app.repositories.repositories import LogRepository, UsuarioRepository

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get("")
def listar_logs(
    tipo_operacao: Optional[str] = Query(default=None),
    current_user=Depends(require_roles("administrador")),
    db: Session = Depends(get_db),
):
    usuario_repository = UsuarioRepository(db)
    logs = LogRepository(db).listar(tipo_operacao=tipo_operacao)

    resultado = []
    for log in logs:
        usuario = usuario_repository.obter_por_id(log.id_usuario) if log.id_usuario else None
        resultado.append({
            "id": log.id,
            "data_hora": log.data_hora,
            "tipo_operacao": log.tipo_operacao,
            "resumo": log.resumo,
            "usuario": usuario.nome if usuario else "Sistema",
            "id_importacao": log.id_importacao,
        })

    return resultado
