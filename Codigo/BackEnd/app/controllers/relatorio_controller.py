"""RelatorioController — gerarRelatorio(filtros) e registrarAgendamento(params).

Cobre UC06 (Gerar relatórios consolidados), UC07 (Agendar relatórios
periódicos) e UC15 (Enviar relatórios agendados).
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.auth import require_roles
from app.db.database import get_db
from app.dtos.schemas import AgendamentoCreateDTO, AgendamentoStatusDTO
from app.services.agendamento_service import AgendamentoService
from app.services.relatorio_service import RelatorioService

router = APIRouter(tags=["Relatorios"])


def _serializar_relatorio(relatorio):
    return {
        "id": relatorio.id,
        "tipo": relatorio.tipo,
        "periodo": relatorio.periodo,
        "caminho_arquivo": relatorio.caminho_arquivo,
        "data_geracao": relatorio.data_geracao,
        "id_usuario_solicitante": relatorio.id_usuario_solicitante,
        "id_agendamento": relatorio.id_agendamento,
    }


def _serializar_agendamento(agendamento):
    return {
        "id": agendamento.id,
        "periodicidade": agendamento.periodicidade,
        "destinatarios": agendamento.destinatarios,
        "filtros": agendamento.filtros,
        "ativo": agendamento.ativo,
        "data_criacao": agendamento.data_criacao,
        "ultimo_envio": agendamento.ultimo_envio,
    }


# ---------------------------------------------------------------------------
# Relatórios (UC06)
# ---------------------------------------------------------------------------

@router.post("/relatorios/gerar")
def gerar_relatorio(
    periodo_inicio: Optional[str] = None,
    periodo_fim: Optional[str] = None,
    regiao: Optional[str] = None,
    categoria: Optional[str] = None,
    current_user=Depends(require_roles("gestor", "administrador")),
    db: Session = Depends(get_db),
):
    """CO06 — gerarRelatorioConsolidado(periodo, filtros)."""

    relatorio, _ = RelatorioService(db).gerar_relatorio(
        usuario_id=current_user.id,
        periodo_inicio=periodo_inicio,
        periodo_fim=periodo_fim,
        regiao=regiao,
        categoria=categoria,
    )
    return _serializar_relatorio(relatorio)


@router.get("/relatorios")
def listar_relatorios(
    current_user=Depends(require_roles("gestor", "administrador", "executivo")),
    db: Session = Depends(get_db),
):
    return [_serializar_relatorio(r) for r in RelatorioService(db).listar_relatorios()]


@router.get("/relatorios/{relatorio_id}/download")
def baixar_relatorio(
    relatorio_id: int,
    current_user=Depends(require_roles("gestor", "administrador", "executivo")),
    db: Session = Depends(get_db),
):
    relatorio = RelatorioService(db).obter_relatorio(relatorio_id)
    if not relatorio or not relatorio.caminho_arquivo:
        raise HTTPException(status_code=404, detail="Relatório não encontrado")

    return FileResponse(
        relatorio.caminho_arquivo,
        media_type="text/csv",
        filename=f"relatorio_{relatorio.id}.csv",
    )


# ---------------------------------------------------------------------------
# Agendamentos (UC07 / UC15)
# ---------------------------------------------------------------------------

@router.post("/agendamentos")
def registrar_agendamento(
    payload: AgendamentoCreateDTO,
    current_user=Depends(require_roles("gestor", "administrador")),
    db: Session = Depends(get_db),
):
    """CO07 — registrarAgendamentoRelatorio(periodicidade, destinatarios, filtros)."""

    agendamento = AgendamentoService(db).registrar_agendamento(
        usuario_id=current_user.id,
        periodicidade=payload.periodicidade,
        destinatarios=payload.destinatarios,
        filtros=payload.filtros,
    )
    return _serializar_agendamento(agendamento)


@router.get("/agendamentos")
def listar_agendamentos(
    current_user=Depends(require_roles("gestor", "administrador")),
    db: Session = Depends(get_db),
):
    return [_serializar_agendamento(a) for a in AgendamentoService(db).listar_agendamentos()]


@router.patch("/agendamentos/{agendamento_id}")
def alterar_status_agendamento(
    agendamento_id: int,
    payload: AgendamentoStatusDTO,
    current_user=Depends(require_roles("gestor", "administrador")),
    db: Session = Depends(get_db),
):
    agendamento = AgendamentoService(db).alterar_status(agendamento_id, payload.ativo)
    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    return _serializar_agendamento(agendamento)


@router.delete("/agendamentos/{agendamento_id}")
def remover_agendamento(
    agendamento_id: int,
    current_user=Depends(require_roles("gestor", "administrador")),
    db: Session = Depends(get_db),
):
    if not AgendamentoService(db).excluir_agendamento(agendamento_id):
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    return {"message": "Agendamento removido com sucesso"}


@router.post("/agendamentos/executar")
def executar_envio_agendado(
    current_user=Depends(require_roles("gestor", "administrador")),
    db: Session = Depends(get_db),
):
    """CO08 — executarEnvioAgendado() (simula o CRON/Scheduler)."""

    envios = AgendamentoService(db).executar_envio_agendado()
    return {
        "message": f"{len(envios)} relatório(s) agendado(s) enviado(s)",
        "envios": envios,
    }
