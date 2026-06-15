

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import require_roles
from app.db.database import get_db
from app.dtos.schemas import MetaCreateDTO
from app.services.meta_service import MetaService

router = APIRouter(prefix="/metas", tags=["Metas"])


@router.post("")
def registrar_meta(
    payload: MetaCreateDTO,
    current_user=Depends(require_roles("gestor", "administrador")),
    db: Session = Depends(get_db),
):
    """CO03 — registrarMeta(periodo, regiao, equipe, valorMeta)."""

    meta = MetaService(db).registrar_meta(
        periodo_inicio=payload.periodo_inicio,
        periodo_fim=payload.periodo_fim,
        regiao=payload.regiao,
        categoria=payload.categoria,
        valor_meta=payload.valor_meta,
        descricao=payload.descricao,
        usuario_id=current_user.id,
    )

    return {
        "id": meta.id,
        "periodo_inicio": meta.periodo_inicio,
        "periodo_fim": meta.periodo_fim,
        "regiao": meta.regiao,
        "categoria": meta.categoria,
        "valor_meta": meta.valor_meta,
        "descricao": meta.descricao,
    }


@router.get("")
def consultar_atingimento_metas(
    current_user=Depends(require_roles("gestor", "administrador", "executivo")),
    db: Session = Depends(get_db),
):
    """CO04 — consultarAtingimentoMetas(filtros)."""

    return MetaService(db).consultar_atingimento_metas()


@router.delete("/{meta_id}")
def remover_meta(
    meta_id: int,
    current_user=Depends(require_roles("gestor", "administrador")),
    db: Session = Depends(get_db),
):
    if not MetaService(db).excluir_meta(meta_id):
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    return {"message": "Meta removida com sucesso"}
