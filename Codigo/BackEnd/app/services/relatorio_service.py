"""RelatorioService — UC06 (Gerar relatórios consolidados).

Conforme o contrato CO06, compila os KPIs e metas do período/filtros
informados e disponibiliza o relatório para visualização ou download.
A geração é registrada em log de auditoria (US13).
"""

import csv
import io
import os
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.db import models
from app.repositories.repositories import LogRepository, RelatorioRepository
from app.services.kpi_service import KPIService
from app.services.meta_service import MetaService

REPORTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "relatorios_gerados",
)


class RelatorioService:
    def __init__(self, db: Session):
        self.db = db
        self.relatorio_repository = RelatorioRepository(db)
        self.log_repository = LogRepository(db)
        self.kpi_service = KPIService(db)
        self.meta_service = MetaService(db)

    def _montar_csv(self, kpis: dict, metas: list[dict]) -> str:
        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter=";")

        writer.writerow(["Relatório Consolidado de Vendas - DashVendas"])
        writer.writerow(["Gerado em", datetime.now().strftime("%d/%m/%Y %H:%M")])
        writer.writerow([])

        writer.writerow(["Resumo Geral"])
        writer.writerow(["Total de vendas", kpis["resumo"]["total_vendas"]])
        writer.writerow(["Quantidade total", kpis["resumo"]["quantidade_total"]])
        writer.writerow(["Total de pedidos", kpis["resumo"]["total_pedidos"]])
        writer.writerow(["Ticket médio", kpis["resumo"]["ticket_medio"]])
        writer.writerow([])

        writer.writerow(["Vendas por Região"])
        writer.writerow(["Região", "Total de vendas", "Quantidade", "Pedidos", "Ticket médio"])
        for item in kpis["por_regiao"]:
            writer.writerow([
                item.get("regiao"),
                item["total_vendas"],
                item["quantidade_total"],
                item["total_pedidos"],
                item["ticket_medio"],
            ])
        writer.writerow([])

        writer.writerow(["Vendas por Categoria"])
        writer.writerow(["Categoria", "Total de vendas", "Quantidade", "Pedidos", "Ticket médio"])
        for item in kpis["por_categoria"]:
            writer.writerow([
                item.get("categoria"),
                item["total_vendas"],
                item["quantidade_total"],
                item["total_pedidos"],
                item["ticket_medio"],
            ])
        writer.writerow([])

        writer.writerow(["Acompanhamento de Metas"])
        writer.writerow(["Período", "Região", "Categoria", "Meta (R$)", "Realizado (R$)", "% Atingido", "Status"])
        for meta in metas:
            writer.writerow([
                f"{meta['periodo_inicio']} a {meta['periodo_fim']}",
                meta.get("regiao") or "-",
                meta.get("categoria") or "-",
                meta["valor_meta"],
                meta["total_realizado"],
                meta["percentual_atingimento"],
                meta["status"],
            ])

        return buffer.getvalue()

    def gerar_relatorio(
        self,
        usuario_id: Optional[int],
        periodo_inicio: Optional[str] = None,
        periodo_fim: Optional[str] = None,
        regiao: Optional[str] = None,
        categoria: Optional[str] = None,
        id_agendamento: Optional[int] = None,
    ):
        """CO06 — gerarRelatorioConsolidado(periodo, filtros)."""

        kpis = self.kpi_service.calcular_kpis(
            periodo_inicio=periodo_inicio,
            periodo_fim=periodo_fim,
            regiao=regiao,
            categoria=categoria,
        )
        metas = self.meta_service.consultar_atingimento_metas()

        conteudo_csv = self._montar_csv(kpis, metas)

        os.makedirs(REPORTS_DIR, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        nome_arquivo = f"relatorio_consolidado_{timestamp}.csv"
        caminho_arquivo = os.path.join(REPORTS_DIR, nome_arquivo)

        with open(caminho_arquivo, "w", encoding="utf-8-sig", newline="") as arquivo:
            arquivo.write(conteudo_csv)

        periodo_label = None
        if periodo_inicio or periodo_fim:
            periodo_label = f"{periodo_inicio or '...'} a {periodo_fim or '...'}"

        relatorio = models.Relatorio(
            tipo="consolidado",
            periodo=periodo_label,
            caminho_arquivo=caminho_arquivo,
            id_usuario_solicitante=usuario_id,
            id_agendamento=id_agendamento,
        )
        relatorio = self.relatorio_repository.salvar(relatorio)

        origem = (
            f"agendamento #{id_agendamento}" if id_agendamento else "sob demanda"
        )
        self.log_repository.registrar(
            tipo_operacao="geracao_relatorio",
            resumo=f"Relatório consolidado #{relatorio.id} gerado ({origem}).",
            usuario_id=usuario_id,
        )

        return relatorio, conteudo_csv

    def listar_relatorios(self) -> list[models.Relatorio]:
        return self.relatorio_repository.listar()

    def obter_relatorio(self, relatorio_id: int):
        return self.relatorio_repository.obter_por_id(relatorio_id)
