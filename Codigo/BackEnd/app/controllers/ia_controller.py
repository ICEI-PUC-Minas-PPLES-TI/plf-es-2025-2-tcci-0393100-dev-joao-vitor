

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import require_roles
from app.db.database import get_db
from app.dtos.schemas import IAAnaliseRequestDTO, IARequestDTO, IAResponseDTO
from app.services.ia_service import IAService

router = APIRouter(prefix="/assistente", tags=["Assistente IA"])


@router.post("/analise", response_model=IAResponseDTO)
def gerar_analise_ia(
    payload: IAAnaliseRequestDTO,
    current_user=Depends(require_roles("executivo", "gestor", "administrador")),
    db: Session = Depends(get_db),
):
    """CO13 — solicitarAnaliseIA(filtros) (UC12)."""

    return IAService(db).gerar_analise(
        periodo_inicio=payload.periodo_inicio,
        periodo_fim=payload.periodo_fim,
        regiao=payload.regiao,
        categoria=payload.categoria,
    )


@router.post("/perguntar", response_model=IAResponseDTO)
def consultar_ia(
    payload: IARequestDTO,
    current_user=Depends(require_roles("executivo", "gestor", "administrador")),
    db: Session = Depends(get_db),
):
    """CO14 — consultarIA(pergunta) (UC13)."""

    return IAService(db).consultar_ia(payload.pergunta)
