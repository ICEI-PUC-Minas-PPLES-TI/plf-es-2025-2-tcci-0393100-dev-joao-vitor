from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.auth import require_roles
from app.services.meta_service import (
    cadastrar_meta,
    listar_metas_com_atingimento,
)

router = APIRouter(prefix="/metas", tags=["Metas"])


class MetaCreate(BaseModel):
    periodo_inicio: str
    periodo_fim: str
    regiao: Optional[str] = None
    categoria: Optional[str] = None
    valor_meta: float = Field(gt=0)


@router.post("")
def criar_meta(
    payload: MetaCreate,
    current_user=Depends(require_roles("gestor", "administrador")),
):
    return cadastrar_meta(
        periodo_inicio=payload.periodo_inicio,
        periodo_fim=payload.periodo_fim,
        regiao=payload.regiao,
        categoria=payload.categoria,
        valor_meta=payload.valor_meta,
    )


@router.get("")
def listar_metas(
    current_user=Depends(require_roles("gestor", "administrador")),
):
    return listar_metas_com_atingimento()