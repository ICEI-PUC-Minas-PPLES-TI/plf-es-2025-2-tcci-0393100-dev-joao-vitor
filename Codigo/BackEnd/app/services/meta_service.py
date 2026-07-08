"""MetaService — UC03 (Definir metas) e UC04 (Acompanhar metas)."""

from typing import Optional

from sqlalchemy.orm import Session

from app.db import models
from app.repositories.repositories import MetaRepository
from app.services.kpi_service import KPIService


class MetaService:
    def __init__(self, db: Session):
        self.db = db
        self.meta_repository = MetaRepository(db)
        self.kpi_service = KPIService(db)

    def registrar_meta(
        self,
        periodo_inicio: str,
        periodo_fim: str,
        regiao: Optional[str],
        categoria: Optional[str],
        valor_meta: float,
        descricao: Optional[str] = None,
        usuario_id: Optional[int] = None,
    ) -> models.Meta:
        """CO03 — registrarMeta(periodo, regiao, equipe, valorMeta)."""

        meta = models.Meta(
            periodo_inicio=periodo_inicio,
            periodo_fim=periodo_fim,
            regiao=regiao,
            categoria=categoria,
            valor_meta=float(valor_meta),
            descricao=descricao,
            id_usuario_responsavel=usuario_id,
        )
        return self.meta_repository.salvar(meta)

    @staticmethod
    def calcular_status_atingimento(percentual: float) -> str:
        if percentual >= 100:
            return "atingida"
        if percentual >= 70:
            return "em_risco"
        return "nao_atingida"

    def consultar_atingimento_metas(self) -> list[dict]:
        """CO04 — consultarAtingimentoMetas(filtros)."""

        resultado = []

        for meta in self.meta_repository.listar():
            kpis = self.kpi_service.calcular_kpis(
                periodo_inicio=meta.periodo_inicio,
                periodo_fim=meta.periodo_fim,
                regiao=meta.regiao,
                categoria=meta.categoria,
            )

            total_vendas = kpis["resumo"]["total_vendas"]

            percentual = (
                total_vendas / meta.valor_meta * 100 if meta.valor_meta > 0 else 0
            )

            resultado.append({
                "id": meta.id,
                "periodo_inicio": meta.periodo_inicio,
                "periodo_fim": meta.periodo_fim,
                "regiao": meta.regiao,
                "categoria": meta.categoria,
                "valor_meta": meta.valor_meta,
                "descricao": meta.descricao,
                "created_at": meta.created_at.strftime("%d/%m/%Y %H:%M") if meta.created_at else None,
                "total_realizado": total_vendas,
                "percentual_atingimento": round(percentual, 2),
                "status": self.calcular_status_atingimento(percentual),
            })

        return resultado

    def excluir_meta(self, meta_id: int) -> bool:
        meta = self.meta_repository.obter_por_id(meta_id)
        if not meta:
            return False
        self.meta_repository.remover(meta)
        return True
