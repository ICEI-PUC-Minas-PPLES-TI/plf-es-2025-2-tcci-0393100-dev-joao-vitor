from datetime import datetime
from typing import Optional

from app.services.kpi_service import consultar_kpis

METAS = []


def cadastrar_meta(
    periodo_inicio: str,
    periodo_fim: str,
    regiao: Optional[str],
    categoria: Optional[str],
    valor_meta: float,
):
    meta = {
        "id": len(METAS) + 1,
        "periodo_inicio": periodo_inicio,
        "periodo_fim": periodo_fim,
        "regiao": regiao,
        "categoria": categoria,
        "valor_meta": float(valor_meta),
        "created_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }

    METAS.insert(0, meta)

    return meta


def calcular_status_atingimento(percentual):
    if percentual >= 100:
        return "atingida"

    if percentual >= 70:
        return "em_risco"

    return "nao_atingida"


def listar_metas_com_atingimento():
    resultado = []

    for meta in METAS:
        kpis = consultar_kpis(
            periodo_inicio=meta["periodo_inicio"],
            periodo_fim=meta["periodo_fim"],
            regiao=meta["regiao"],
            categoria=meta["categoria"],
        )

        total_vendas = kpis["resumo"]["total_vendas"]

        percentual = (
            total_vendas / meta["valor_meta"] * 100
            if meta["valor_meta"] > 0
            else 0
        )

        resultado.append({
            **meta,
            "total_realizado": total_vendas,
            "percentual_atingimento": round(percentual, 2),
            "status": calcular_status_atingimento(percentual),
        })

    return resultado