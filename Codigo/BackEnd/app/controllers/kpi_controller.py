
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import require_roles
from app.db.database import get_db
from app.dtos.schemas import KPIResponseDTO
from app.services.kpi_service import KPIService

router = APIRouter(prefix="/kpis", tags=["KPIs"])


@router.get("", response_model=KPIResponseDTO)
def consultar_kpis(
    periodo_inicio: Optional[str] = Query(default=None),
    periodo_fim: Optional[str] = Query(default=None),
    regiao: Optional[str] = Query(default=None),
    categoria: Optional[str] = Query(default=None),
    current_user=Depends(require_roles("gestor", "administrador", "executivo")),
    db: Session = Depends(get_db),
):
    """CO02 — consultarKPIs(periodo, filtros)."""

    return KPIService(db).calcular_kpis(
        periodo_inicio=periodo_inicio,
        periodo_fim=periodo_fim,
        regiao=regiao,
        categoria=categoria,
    )
