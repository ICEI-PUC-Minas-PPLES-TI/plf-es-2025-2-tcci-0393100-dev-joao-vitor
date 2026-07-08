"""ValidacaoPlanilhaService — UC09 (Validar dados importados).

Conforme a Seção 3.4 da documentação, este serviço aplica o padrão
Template Method: o método validar_planilha() define a sequência fixa
de etapas do algoritmo (leitura dos registros, verificação estrutural,
validação de campos, identificação de inconsistências e geração de um
resumo), enquanto validações específicas são executadas pelo método
auxiliar validar_item(), que pode ser especializado por subclasses.
"""

import json
from abc import ABC
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session

from app.db import models
from app.repositories.repositories import ImportacaoRepository, LogRepository
from app.services.importacao_service import normalize_text


class ValidacaoPlanilhaTemplate(ABC):
    """Classe base do Template Method de validação."""

    def __init__(self, db: Session):
        self.db = db
        self.importacao_repository = ImportacaoRepository(db)
        self.log_repository = LogRepository(db)

    # ------------------------------------------------------------------
    # Template Method — fluxo fixo
    # ------------------------------------------------------------------
    def validar_planilha(self, importacao_id: int, usuario) -> dict:
        """CO10 — validarPlanilha(idPlanilha)."""

        importacao = self._ler_registros(importacao_id)
        itens = self.importacao_repository.listar_itens(importacao_id)

        self._verificar_estrutura(importacao, itens)

        chaves_processadas: dict = {}
        validos = 0
        invalidos = 0
        inconsistencias = []

        for item in itens:
            dados = json.loads(item.dados_json or "{}")
            erros = self.validar_item(dados)

            # Detecção de duplicidade DENTRO da mesma planilha.
            # A chave combina os campos de negócio do registro. Quando a
            # mesma combinação aparece mais de uma vez, as ocorrências
            # seguintes são marcadas como duplicadas, registrando a linha
            # original para rastreabilidade.
            chave = self._chave_duplicidade(dados)
            if chave in chaves_processadas:
                erros.append(f"registro duplicado (igual à linha {chaves_processadas[chave]})")
            else:
                chaves_processadas[chave] = item.linha

            if erros:
                item.status = "invalido"
                item.mensagem_erro = "; ".join(erros)
                invalidos += 1
                inconsistencias.append({
                    "linha": item.linha,
                    "produto": dados.get("produto"),
                    "erros": erros,
                })
            else:
                item.status = "valido"
                item.mensagem_erro = None
                item.quantidade = float(dados.get("quantidade"))
                item.valor = float(dados.get("valor_total"))
                validos += 1

            self.db.add(item)

        resumo = self._gerar_resumo(importacao, validos, invalidos)

        importacao.status = "validada" if invalidos == 0 else "validada_com_alertas"
        importacao.observacao = resumo
        self.db.add(importacao)
        self.db.commit()

        self.log_repository.registrar(
            tipo_operacao="validacao_planilha",
            resumo=resumo,
            usuario_id=usuario.id,
            importacao_id=importacao.id,
        )

        return {
            "importacao": importacao,
            "total_registros": len(itens),
            "total_validos": validos,
            "total_invalidos": invalidos,
            "registros_invalidos": inconsistencias,
            "resumo": resumo,
        }

    # ------------------------------------------------------------------
    # Etapas do template
    # ------------------------------------------------------------------
    def _ler_registros(self, importacao_id: int) -> models.Importacao:
        importacao = self.importacao_repository.obter_por_id(importacao_id)
        if not importacao:
            raise ValueError("Importação não encontrada")
        return importacao

    def _verificar_estrutura(self, importacao: models.Importacao, itens: list) -> None:
        if not itens:
            raise ValueError("A importação não possui registros para validar")

    def _chave_duplicidade(self, dados: dict) -> tuple:
        """Chave que identifica um registro de venda como duplicado.

        Combina os principais campos de negócio. Quanto mais campos na
        chave, mais específica (e menos agressiva) é a detecção: dois
        registros só são considerados duplicados quando coincidem em
        TODOS estes campos — o que, em uma base real, corresponde de fato
        ao mesmo lançamento repetido.
        """
        return (
            str(dados.get("data_venda") or ""),
            normalize_text(dados.get("vendedor")),
            normalize_text(dados.get("regiao")),
            normalize_text(dados.get("produto")),
            normalize_text(dados.get("categoria")),
            str(dados.get("quantidade") or ""),
            str(dados.get("valor_unitario") or ""),
            str(dados.get("valor_total") or ""),
        )

    def _gerar_resumo(self, importacao, validos: int, invalidos: int) -> str:
        return (
            f"Validação da planilha '{importacao.nome_arquivo}': "
            f"{validos} registros válidos; {invalidos} registros inválidos."
        )

    # ------------------------------------------------------------------
    # Hook especializável (validar_item)
    # ------------------------------------------------------------------
    def validar_item(self, dados: dict) -> list[str]:
        """Valida um item individual da planilha. Retorna a lista de erros."""

        erros: list[str] = []

        self._validar_data(dados.get("data_venda"), erros)

        for campo in ("vendedor", "regiao", "produto", "categoria"):
            valor = dados.get(campo)
            if valor is None or str(valor).strip() == "":
                erros.append(f"{campo} ausente")

        quantidade = self._validar_numero(dados.get("quantidade"), "quantidade", erros)
        valor_unitario = self._validar_numero(dados.get("valor_unitario"), "valor_unitario", erros)
        valor_total = self._validar_numero(dados.get("valor_total"), "valor_total", erros)

        if quantidade and valor_unitario and valor_total:
            valor_calculado = round(quantidade * valor_unitario, 2)
            if abs(valor_calculado - valor_total) > 0.05:
                erros.append("valor_total incompatível com quantidade x valor_unitario")

        return erros

    # ------------------------------------------------------------------
    # Auxiliares
    # ------------------------------------------------------------------
    def _validar_numero(self, valor: Any, campo: str, erros: list[str]):
        if valor is None or valor == "":
            erros.append(f"{campo} ausente")
            return None

        try:
            numero = float(valor)
        except (TypeError, ValueError):
            erros.append(f"{campo} inválido")
            return None

        if numero <= 0:
            erros.append(f"{campo} deve ser maior que zero")
            return None

        return numero

    def _validar_data(self, valor: Any, erros: list[str]):
        if valor is None or str(valor).strip() == "":
            erros.append("data_venda ausente")
            return None

        try:
            return pd.to_datetime(valor, dayfirst=True)
        except Exception:
            erros.append("data_venda inválida")
            return None


class ValidacaoPlanilhaService(ValidacaoPlanilhaTemplate):
    """Implementação concreta padrão da validação de planilhas."""
