"""IAService — UC12 (Análises interpretativas) e UC13 (Linguagem natural).

Conforme os contratos CO13 e CO14, encapsula a geração de análises
interpretativas e respostas em linguagem natural com base nos KPIs e
metas calculados. O acesso ao provedor externo é mediado pelo
IAGateway (padrão Adapter); na ausência de provedor configurado, o
serviço gera as respostas localmente a partir dos dados reais.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.integrations.ia_gateway import IAGateway, LocalIAGateway, OpenAIGateway
from app.repositories.repositories import ProdutoRepository, RegiaoRepository
from app.services.kpi_service import KPIService
from app.services.meta_service import MetaService


def _formatar_moeda(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class IAService:
    def __init__(self, db: Session, gateway: Optional[IAGateway] = None):
        self.db = db
        self.kpi_service = KPIService(db)
        self.meta_service = MetaService(db)
        self.regiao_repository = RegiaoRepository(db)
        self.produto_repository = ProdutoRepository(db)

        if gateway is not None:
            self.gateway = gateway
        else:
            externo = OpenAIGateway()
            self.gateway = externo if externo.esta_configurado() else LocalIAGateway()

    # ------------------------------------------------------------------
    # UC12 — gerarAnaliseIA(filtros)
    # ------------------------------------------------------------------
    def gerar_analise(
        self,
        periodo_inicio: Optional[str] = None,
        periodo_fim: Optional[str] = None,
        regiao: Optional[str] = None,
        categoria: Optional[str] = None,
    ) -> dict:
        """CO13 — solicitarAnaliseIA(filtros)."""

        kpis = self.kpi_service.calcular_kpis(
            periodo_inicio=periodo_inicio,
            periodo_fim=periodo_fim,
            regiao=regiao,
            categoria=categoria,
        )
        metas = self.meta_service.consultar_atingimento_metas()

        contexto = {"kpis": kpis, "metas": metas}

        prompt = (
            "Gere uma análise interpretativa do desempenho de vendas, "
            "destacando tendências, variações e riscos de metas."
        )

        resposta_externa = self.gateway.gerar_resposta(prompt, contexto)
        if resposta_externa:
            return {
                "resposta": resposta_externa,
                "contexto": {"tipo": "analise", "filtros": kpis["filtros"]},
                "dados": kpis["resumo"],
                "provedor": self.gateway.nome,
            }

        return {
            "resposta": self._analise_local(kpis, metas),
            "contexto": {"tipo": "analise", "filtros": kpis["filtros"]},
            "dados": kpis["resumo"],
            "provedor": "local",
        }

    def _analise_local(self, kpis: dict, metas: list[dict]) -> str:
        resumo = kpis["resumo"]

        if resumo["total_pedidos"] == 0:
            return (
                "Não há vendas registradas para os filtros informados. "
                "Importe uma planilha de vendas para habilitar as análises."
            )

        partes = [
            f"No período analisado, o total de vendas foi de {_formatar_moeda(resumo['total_vendas'])}, "
            f"distribuído em {resumo['total_pedidos']} pedidos, com ticket médio de "
            f"{_formatar_moeda(resumo['ticket_medio'])}."
        ]

        por_regiao = sorted(kpis["por_regiao"], key=lambda x: x["total_vendas"], reverse=True)
        if por_regiao:
            lider = por_regiao[0]
            participacao = (
                lider["total_vendas"] / resumo["total_vendas"] * 100
                if resumo["total_vendas"] else 0
            )
            partes.append(
                f"A região {lider['regiao']} lidera o desempenho, com "
                f"{_formatar_moeda(lider['total_vendas'])} "
                f"({participacao:.1f}% do total)."
            )
            if len(por_regiao) > 1:
                lanterna = por_regiao[-1]
                partes.append(
                    f"A região {lanterna['regiao']} apresenta o menor volume "
                    f"({_formatar_moeda(lanterna['total_vendas'])}), podendo demandar atenção."
                )

        por_categoria = sorted(kpis["por_categoria"], key=lambda x: x["total_vendas"], reverse=True)
        if por_categoria:
            partes.append(
                f"Entre as categorias, {por_categoria[0]['categoria']} concentra o maior faturamento "
                f"({_formatar_moeda(por_categoria[0]['total_vendas'])})."
            )

        em_risco = [m for m in metas if m["status"] != "atingida"]
        if metas:
            if em_risco:
                partes.append(
                    f"Das {len(metas)} metas cadastradas, {len(em_risco)} estão em risco ou não atingidas, "
                    "recomendando-se ações corretivas nos segmentos correspondentes."
                )
            else:
                partes.append("Todas as metas cadastradas foram atingidas no período.")

        return " ".join(partes)

    # ------------------------------------------------------------------
    # UC13 — consultarIA(pergunta)
    # ------------------------------------------------------------------
    def consultar_ia(self, pergunta: str) -> dict:
        """CO14 — consultarIA(pergunta)."""

        pergunta_lower = pergunta.lower().strip()

        regiao = self._extrair_regiao(pergunta_lower)
        categoria = self._extrair_categoria(pergunta_lower)

        kpis = self.kpi_service.calcular_kpis(regiao=regiao, categoria=categoria)
        metas = self.meta_service.consultar_atingimento_metas()

        contexto_externo = {"kpis": kpis, "metas": metas}
        resposta_externa = self.gateway.gerar_resposta(pergunta, contexto_externo)
        if resposta_externa:
            return {
                "pergunta": pergunta,
                "resposta": resposta_externa,
                "contexto": {"regiao": regiao, "categoria": categoria},
                "provedor": self.gateway.nome,
            }

        return self._responder_local(pergunta, pergunta_lower, regiao, categoria, kpis, metas)

    def _extrair_regiao(self, pergunta_lower: str) -> Optional[str]:
        for regiao in self.regiao_repository.listar():
            if regiao.nome.lower() in pergunta_lower:
                return regiao.nome
        return None

    def _extrair_categoria(self, pergunta_lower: str) -> Optional[str]:
        for categoria in self.produto_repository.listar_categorias():
            if categoria.lower() in pergunta_lower:
                return categoria
        return None

    def _responder_local(self, pergunta, pergunta_lower, regiao, categoria, kpis, metas) -> dict:
        resumo = kpis["resumo"]

        contexto_partes = []
        if regiao:
            contexto_partes.append(f"na região {regiao}")
        if categoria:
            contexto_partes.append(f"na categoria {categoria}")
        contexto = " " + " e ".join(contexto_partes) if contexto_partes else ""

        # Perguntas sobre metas
        if any(p in pergunta_lower for p in ["meta", "metas", "atingiu", "atingimento"]):
            if not metas:
                resposta = "Ainda não há metas cadastradas no sistema."
            else:
                metas_filtradas = [
                    m for m in metas
                    if (not regiao or (m["regiao"] or "").lower() == regiao.lower())
                    and (not categoria or (m["categoria"] or "").lower() == categoria.lower())
                ] or metas

                linhas = [
                    f"- Período {m['periodo_inicio']} a {m['periodo_fim']}: "
                    f"{m['percentual_atingimento']}% da meta de "
                    f"{_formatar_moeda(m['valor_meta'])} ({m['status'].replace('_', ' ')})"
                    for m in metas_filtradas[:5]
                ]
                resposta = f"Acompanhamento de metas{contexto}:\n" + "\n".join(linhas)

            return {
                "pergunta": pergunta,
                "resposta": resposta,
                "contexto": {"regiao": regiao, "categoria": categoria, "tipo": "metas"},
                "provedor": "local",
            }

        # Perguntas de ranking
        if any(p in pergunta_lower for p in ["melhor", "top", "ranking", "maior", "pior", "menor"]):
            reverso = not any(p in pergunta_lower for p in ["pior", "menor"])

            if "vendedor" in pergunta_lower:
                ranking, chave = kpis["por_vendedor"], "vendedor"
            elif "regiao" in pergunta_lower or "região" in pergunta_lower:
                ranking, chave = kpis["por_regiao"], "regiao"
            else:
                ranking, chave = kpis["por_categoria"], "categoria"

            ranking = sorted(ranking, key=lambda x: x["total_vendas"], reverse=reverso)

            if not ranking:
                resposta = f"Não encontrei dados de vendas{contexto} para montar um ranking."
            else:
                linhas = [
                    f"- {item.get(chave) or 'Não informado'}: {_formatar_moeda(item['total_vendas'])}"
                    for item in ranking[:3]
                ]
                resposta = "Ranking por total de vendas:\n" + "\n".join(linhas)

            return {
                "pergunta": pergunta,
                "resposta": resposta,
                "contexto": {"regiao": regiao, "categoria": categoria, "tipo": "ranking"},
                "provedor": "local",
            }

        # Resumo geral
        if resumo["total_pedidos"] == 0:
            resposta = f"Ainda não há vendas registradas{contexto}."
        else:
            resposta = (
                f"O total de vendas{contexto} é de {_formatar_moeda(resumo['total_vendas'])}, "
                f"em {resumo['total_pedidos']} pedidos, com ticket médio de "
                f"{_formatar_moeda(resumo['ticket_medio'])}."
            )

        return {
            "pergunta": pergunta,
            "resposta": resposta,
            "contexto": {"regiao": regiao, "categoria": categoria, "tipo": "resumo"},
            "dados": resumo,
            "provedor": "local",
        }
