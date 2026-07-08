"""AlertaService — UC05 (Receber alertas de desempenho).

Conforme o contrato CO05, verifica regras configuradas (status das
metas) e gera/retorna os alertas pertinentes ao gestor.
"""

from sqlalchemy.orm import Session

from app.db import models
from app.repositories.repositories import AlertaRepository
from app.services.meta_service import MetaService


class AlertaService:
    def __init__(self, db: Session):
        self.db = db
        self.alerta_repository = AlertaRepository(db)
        self.meta_service = MetaService(db)

    def gerar_alertas(self) -> list[models.Alerta]:
        """Analisa as metas e gera alertas para as em risco/não atingidas."""

        metas = self.meta_service.consultar_atingimento_metas()
        novos_alertas = []

        for meta in metas:
            if meta["status"] == "atingida":
                continue

            periodo_referencia = f"{meta['periodo_inicio']} a {meta['periodo_fim']}"
            nivel = "alto" if meta["status"] == "nao_atingida" else "medio"

            descricao_meta = meta.get("descricao") or "Meta de vendas"
            contexto = []
            if meta.get("regiao"):
                contexto.append(f"região {meta['regiao']}")
            if meta.get("categoria"):
                contexto.append(f"categoria {meta['categoria']}")
            contexto_str = f" ({', '.join(contexto)})" if contexto else ""

            mensagem = (
                f"{descricao_meta}{contexto_str}: atingiu "
                f"{meta['percentual_atingimento']}% da meta de "
                f"R$ {meta['valor_meta']:.2f} no período {periodo_referencia}."
            )

            if self.alerta_repository.existe_alerta("meta_em_risco", periodo_referencia, mensagem):
                continue

            alerta = models.Alerta(
                tipo="meta_em_risco",
                mensagem=mensagem,
                nivel_criticidade=nivel,
                periodo_referencia=periodo_referencia,
            )
            self.alerta_repository.adicionar(alerta)
            novos_alertas.append(alerta)

        if novos_alertas:
            self.alerta_repository.commit()

        return novos_alertas

    def consultar_alertas(self, apenas_nao_lidos: bool = False) -> list[models.Alerta]:
        """CO05 — consultarAlertas(periodo, filtros)."""
        self.gerar_alertas()
        return self.alerta_repository.listar(apenas_nao_lidos=apenas_nao_lidos)

    def marcar_como_lido(self, alerta_id: int):
        alerta = self.alerta_repository.obter_por_id(alerta_id)
        if not alerta:
            return None

        alerta.lido = True
        self.db.commit()
        self.db.refresh(alerta)
        return alerta
