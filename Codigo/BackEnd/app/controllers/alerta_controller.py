from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import require_roles
from app.db.database import get_db
from app.services.alerta_service import AlertaService

router = APIRouter(prefix="/alertas", tags=["Alertas"])


def _serializar(alerta):
    return {
        "id": alerta.id,
        "tipo": alerta.tipo,
        "mensagem": alerta.mensagem,
        "nivel_criticidade": alerta.nivel_criticidade,
        "periodo_referencia": alerta.periodo_referencia,
        "created_at": alerta.created_at,
        "lido": alerta.lido,
    }


@router.get("")
def consultar_alertas(
    apenas_nao_lidos: Optional[bool] = False,
    current_user=Depends(require_roles("gestor", "administrador", "executivo")),
    db: Session = Depends(get_db),
):
    """CO05 — consultarAlertas(periodo, filtros)."""

    alertas = AlertaService(db).consultar_alertas(apenas_nao_lidos=apenas_nao_lidos)
    return [_serializar(a) for a in alertas]


@router.patch("/{alerta_id}/lido")
def marcar_como_lido(
    alerta_id: int,
    current_user=Depends(require_roles("gestor", "administrador", "executivo")),
    db: Session = Depends(get_db),
):
    alerta = AlertaService(db).marcar_como_lido(alerta_id)
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    return _serializar(alerta)
