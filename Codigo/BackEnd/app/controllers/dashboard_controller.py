

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, require_roles
from app.db.database import get_db
from app.services.kpi_service import KPIService
from app.services.meta_service import MetaService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def get_summary(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    kpis = KPIService(db).calcular_kpis()
    resumo = kpis["resumo"]

    metas = MetaService(db).consultar_atingimento_metas()
    meta_percentual = (
        round(sum(m["percentual_atingimento"] for m in metas) / len(metas), 2)
        if metas
        else 0.0
    )

    return {
        "usuario": {
            "id": current_user.id,
            "nome": current_user.nome,
            "role": current_user.tipo_usuario,
        },
        "resumo": {
            "total_vendas": resumo["total_vendas"],
            "total_pedidos": resumo["total_pedidos"],
            "ticket_medio": resumo["ticket_medio"],
            "meta_percentual": meta_percentual,
        },
        "por_regiao": kpis["por_regiao"],
        "por_categoria": kpis["por_categoria"],
    }


@router.get("/desempenho-individual")
def consultar_desempenho_individual(
    periodo_inicio: Optional[str] = Query(default=None),
    periodo_fim: Optional[str] = Query(default=None),
    current_user=Depends(require_roles("vendedor", "gestor", "administrador")),
    db: Session = Depends(get_db),
):
    """CO01 — solicitarDesempenhoIndividual() (UC01)."""

    kpis = KPIService(db).calcular_kpis(
        periodo_inicio=periodo_inicio,
        periodo_fim=periodo_fim,
        vendedor=current_user.nome,
    )

    return {
        "vendedor": current_user.nome,
        "resumo": kpis["resumo"],
        "por_categoria": kpis["por_categoria"],
        "por_regiao": kpis["por_regiao"],
        "filtros": kpis["filtros"],
    }
