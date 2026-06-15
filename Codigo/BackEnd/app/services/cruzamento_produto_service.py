"""CruzamentoProdutoService — UC10 (Cruzar produtos).

Conforme o contrato CO11, associa os itens validados da planilha aos
produtos do cadastro interno, por código ou similaridade textual, e
consolida as vendas válidas na base de dados.

Otimização para catálogos grandes
----------------------------------
O catálogo de produtos pode conter dezenas de milhares de itens. Para
evitar comparar cada item da planilha contra todo o catálogo (custo
quadrático), o serviço constrói, uma única vez por cruzamento, índices
em memória:

  - índice por código interno normalizado;
  - índice por descrição normalizada.

A correspondência exata (código ou descrição) é resolvida em tempo
constante por esses índices. A busca por similaridade textual — mais
custosa — só é executada quando não há correspondência exata, servindo
como mecanismo de tolerância a pequenas variações de digitação.
"""

import json
from difflib import SequenceMatcher

import pandas as pd
from sqlalchemy.orm import Session

from app.db import models
from app.repositories.repositories import (
    ImportacaoRepository,
    LogRepository,
    ProdutoRepository,
    RegiaoRepository,
)
from app.services.importacao_service import normalize_text

SIMILARIDADE_MINIMA = 0.75

# Acima deste tamanho de catálogo, a busca por similaridade (custosa) é
# desativada e o cruzamento usa apenas correspondência exata (código ou
# descrição), garantindo desempenho adequado em bases reais grandes.
LIMITE_SIMILARIDADE_CATALOGO = 3000


def calcular_similaridade(texto_a, texto_b) -> float:
    texto_a = normalize_text(texto_a).replace("_", " ")
    texto_b = normalize_text(texto_b).replace("_", " ")

    if not texto_a or not texto_b:
        return 0.0

    return SequenceMatcher(None, texto_a, texto_b).ratio()


class CruzamentoProdutoService:
    def __init__(self, db: Session):
        self.db = db
        self.importacao_repository = ImportacaoRepository(db)
        self.produto_repository = ProdutoRepository(db)
        self.regiao_repository = RegiaoRepository(db)
        self.log_repository = LogRepository(db)

        # Índices construídos sob demanda (lazy) na primeira consulta.
        self._produtos = None
        self._idx_codigo = None
        self._idx_descricao = None

    # ------------------------------------------------------------------
    # Índices em memória
    # ------------------------------------------------------------------
    def _garantir_indices(self) -> None:
        if self._produtos is not None:
            return

        self._produtos = self.produto_repository.listar()
        self._idx_codigo = {}
        self._idx_descricao = {}

        for produto in self._produtos:
            chave_cod = normalize_text(produto.codigo_interno)
            chave_desc = normalize_text(produto.descricao)
            # O primeiro a registrar a chave prevalece (catálogo é único
            # por código; descrições repetidas apontam para o 1º produto).
            self._idx_codigo.setdefault(chave_cod, produto)
            self._idx_descricao.setdefault(chave_desc, produto)

    def _resposta(self, produto, confianca: float, status: str) -> dict:
        if produto is None:
            return {
                "produto_id": None,
                "produto_cadastrado": None,
                "categoria_cadastrada": None,
                "confianca_cruzamento": round(confianca, 2),
                "status_cruzamento": status,
            }
        return {
            "produto_id": produto.id,
            "produto_cadastrado": produto.descricao,
            "categoria_cadastrada": produto.categoria,
            "confianca_cruzamento": round(confianca, 2),
            "status_cruzamento": status,
        }

    # ------------------------------------------------------------------
    # Cruzamento de um produto
    # ------------------------------------------------------------------
    def cruzar_produto(self, nome_produto: str) -> dict:
        """Cruza um único nome de produto contra o cadastro interno."""

        self._garantir_indices()
        chave = normalize_text(nome_produto)

        # 1) Correspondência exata por código interno.
        produto = self._idx_codigo.get(chave)
        if produto is not None:
            return self._resposta(produto, 1.0, "encontrado")

        # 2) Correspondência exata por descrição.
        produto = self._idx_descricao.get(chave)
        if produto is not None:
            return self._resposta(produto, 1.0, "encontrado")

        # 3) Similaridade textual (somente para catálogos menores).
        if len(self._produtos) <= LIMITE_SIMILARIDADE_CATALOGO:
            melhor_produto = None
            maior_score = 0.0
            for prod in self._produtos:
                score = calcular_similaridade(nome_produto, prod.descricao)
                if score > maior_score:
                    maior_score = score
                    melhor_produto = prod

            if melhor_produto and maior_score >= SIMILARIDADE_MINIMA:
                return self._resposta(melhor_produto, maior_score, "encontrado")

            return self._resposta(None, maior_score, "nao_encontrado")

        # Catálogo grande: sem similaridade, apenas correspondência exata.
        return self._resposta(None, 0.0, "nao_encontrado")

    # ------------------------------------------------------------------
    # Cruzamento da planilha inteira
    # ------------------------------------------------------------------
    def cruzar_produtos(self, importacao_id: int, usuario) -> dict:
        """CO11 — executarCruzamentoProdutos(idPlanilha).

        Pré-condição: a planilha deve ter sido validada (UC09).
        Pós-condição: itens associados a produtos internos e vendas
        válidas consolidadas na base.
        """

        importacao = self.importacao_repository.obter_por_id(importacao_id)
        if not importacao:
            raise ValueError("Importação não encontrada")

        if importacao.status not in ("validada", "validada_com_alertas"):
            raise ValueError(
                "A planilha precisa ser validada antes do cruzamento de produtos"
            )

        # Constrói os índices uma única vez para toda a planilha.
        self._garantir_indices()

        itens = self.importacao_repository.listar_itens(importacao_id)
        itens_validos = [item for item in itens if item.status == "valido"]

        encontrados = 0
        nao_encontrados = 0
        registros_processados = []

        for item in itens_validos:
            dados = json.loads(item.dados_json or "{}")

            resultado = self.cruzar_produto(dados.get("produto") or "")

            item.id_produto = resultado["produto_id"]
            item.confianca_cruzamento = resultado["confianca_cruzamento"]
            item.status_cruzamento = resultado["status_cruzamento"]
            self.db.add(item)

            if resultado["status_cruzamento"] == "encontrado":
                encontrados += 1
            else:
                nao_encontrados += 1

            # Consolida a venda na base (alimenta KPIs, metas e dashboards)
            regiao = self.regiao_repository.obter_ou_criar(str(dados.get("regiao") or ""))
            data_venda = pd.to_datetime(dados.get("data_venda"), dayfirst=True).date()

            venda = models.Venda(
                data_venda=data_venda,
                quantidade=float(dados.get("quantidade")),
                valor_total=float(dados.get("valor_total")),
                vendedor_nome=str(dados.get("vendedor")),
                regiao_nome=str(dados.get("regiao")),
                produto_nome=str(dados.get("produto")),
                categoria_nome=resultado["categoria_cadastrada"] or str(dados.get("categoria")),
                id_regiao=regiao.id if regiao else None,
                id_produto=resultado["produto_id"],
            )
            self.db.add(venda)

            registros_processados.append({
                "linha": item.linha,
                "produto": dados.get("produto"),
                "produto_cadastrado": resultado["produto_cadastrado"],
                "status_cruzamento": resultado["status_cruzamento"],
                "confianca_cruzamento": resultado["confianca_cruzamento"],
            })

        resumo = (
            f"Cruzamento da planilha '{importacao.nome_arquivo}': "
            f"{encontrados} produtos encontrados; {nao_encontrados} não encontrados. "
            f"{len(itens_validos)} vendas consolidadas."
        )

        importacao.status = "processada"
        importacao.observacao = resumo
        self.db.add(importacao)
        self.db.commit()

        self.log_repository.registrar(
            tipo_operacao="cruzamento_produtos",
            resumo=resumo,
            usuario_id=usuario.id,
            importacao_id=importacao.id,
        )

        return {
            "importacao": importacao,
            "total_itens": len(itens_validos),
            "encontrados": encontrados,
            "nao_encontrados": nao_encontrados,
            "criterio_similaridade_minima": SIMILARIDADE_MINIMA,
            "registros_processados": registros_processados,
            "resumo": resumo,
        }
