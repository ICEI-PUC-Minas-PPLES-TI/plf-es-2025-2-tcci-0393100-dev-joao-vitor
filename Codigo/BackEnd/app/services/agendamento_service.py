"""AgendamentoService — UC07 (Agendar relatórios) e UC15 (Enviar agendados).

Conforme os contratos CO07 e CO08, registra agendamentos com
periodicidade, destinatários e filtros, e coordena a execução
automática: identifica agendamentos ativos e dispara gerarRelatorio()
do RelatorioService, registrando cada envio em log interno (abordagem
orientada a eventos descrita na Seção 3.4).
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.db import models
from app.repositories.repositories import AgendamentoRepository, LogRepository
from app.services.relatorio_service import RelatorioService


class AgendamentoService:
    def __init__(self, db: Session):
        self.db = db
        self.agendamento_repository = AgendamentoRepository(db)
        self.log_repository = LogRepository(db)
        self.relatorio_service = RelatorioService(db)

    def registrar_agendamento(
        self,
        usuario_id: int,
        periodicidade: str,
        destinatarios: str,
        filtros: Optional[str] = None,
    ) -> models.AgendamentoRelatorio:
        """CO07 — registrarAgendamentoRelatorio(periodicidade, destinatarios, filtros)."""

        agendamento = models.AgendamentoRelatorio(
            periodicidade=periodicidade,
            destinatarios=destinatarios,
            filtros=filtros,
            id_usuario_criador=usuario_id,
        )
        return self.agendamento_repository.salvar(agendamento)

    def listar_agendamentos(self) -> list[models.AgendamentoRelatorio]:
        return self.agendamento_repository.listar()

    def alterar_status(self, agendamento_id: int, ativo: bool):
        agendamento = self.agendamento_repository.obter_por_id(agendamento_id)
        if not agendamento:
            return None

        agendamento.ativo = ativo
        self.db.commit()
        self.db.refresh(agendamento)
        return agendamento

    def excluir_agendamento(self, agendamento_id: int) -> bool:
        agendamento = self.agendamento_repository.obter_por_id(agendamento_id)
        if not agendamento:
            return False
        self.agendamento_repository.remover(agendamento)
        return True

    def executar_envio_agendado(self) -> list[dict]:
        """CO08 — executarEnvioAgendado().

        Simula o Executor de Tarefas Agendadas (CRON/Scheduler) do
        diagrama de arquitetura: para cada agendamento ativo, gera o
        relatório, registra o envio aos destinatários e grava o log.
        """

        agendamentos = self.agendamento_repository.listar_ativos()
        envios = []

        for agendamento in agendamentos:
            relatorio, _ = self.relatorio_service.gerar_relatorio(
                usuario_id=agendamento.id_usuario_criador,
                id_agendamento=agendamento.id,
            )

            agendamento.ultimo_envio = datetime.utcnow()
            self.db.add(agendamento)

            self.log_repository.registrar(
                tipo_operacao="envio_relatorio_agendado",
                resumo=(
                    f"Relatório #{relatorio.id} enviado para "
                    f"{agendamento.destinatarios} (agendamento #{agendamento.id})."
                ),
                usuario_id=agendamento.id_usuario_criador,
            )

            envios.append({
                "agendamento_id": agendamento.id,
                "relatorio_id": relatorio.id,
                "destinatarios": agendamento.destinatarios,
                "enviado_em": agendamento.ultimo_envio,
            })

        if envios:
            self.db.commit()

        return envios
