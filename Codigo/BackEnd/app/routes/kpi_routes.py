from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.core.auth import require_roles
from app.services.kpi_service import consultar_kpis

router = APIRouter(prefix="/kpis", tags=["KPIs"])


@router.get("")
def get_kpis(
    periodo_inicio: Optional[str] = Query(default=None),
    periodo_fim: Optional[str] = Query(default=None),
    regiao: Optional[str] = Query(default=None),
    categoria: Optional[str] = Query(default=None),
    current_user=Depends(require_roles("gestor", "administrador")),
):
    return consultar_kpis(
        periodo_inicio=periodo_inicio,
        periodo_fim=periodo_fim,
        regiao=regiao,
        categoria=categoria,
    )