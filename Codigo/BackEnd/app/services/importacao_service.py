"""ImportacaoService — UC08 (Importar planilha Excel).

Conforme o contrato CO09, a importação armazena a planilha no sistema
(registros brutos como ImportacaoItem) e a deixa disponível para a
etapa de validação posterior (UC09).
"""

import io
import json
import re
import unicodedata
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session

from app.db import models
from app.repositories.repositories import ImportacaoRepository, LogRepository

REQUIRED_COLUMNS = [
    "data_venda",
    "vendedor",
    "regiao",
    "produto",
    "categoria",
    "quantidade",
    "valor_unitario",
    "valor_total",
]


def normalize_text(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""

    text = str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^a-z0-9_]", "", text)
    return text


def normalize_columns(columns):
    return [normalize_text(col) for col in columns]


class ImportacaoService:
    def __init__(self, db: Session):
        self.db = db
        self.importacao_repository = ImportacaoRepository(db)
        self.log_repository = LogRepository(db)

    def importar_planilha(self, file_bytes: bytes, filename: str, usuario) -> models.Importacao:
        """CO09 — importarPlanilha(arquivoExcel)."""

        try:
            df = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
        except Exception as exc:
            raise ValueError(f"Erro ao ler o arquivo Excel: {str(exc)}") from exc

        if df.empty:
            raise ValueError("A planilha está vazia")

        df.columns = normalize_columns(df.columns)

        missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            raise ValueError(
                f"Colunas obrigatórias ausentes: {', '.join(missing_columns)}"
            )

        df = df[REQUIRED_COLUMNS].copy().dropna(how="all")

        importacao = models.Importacao(
            nome_arquivo=filename,
            status="importada",
            observacao=f"{len(df)} registros recebidos. Aguardando validação.",
            id_usuario=usuario.id,
        )
        self.db.add(importacao)
        self.db.flush()

        for idx, row in df.iterrows():
            linha_excel = idx + 2

            dados = {}
            for col in REQUIRED_COLUMNS:
                valor = row[col]
                if pd.isna(valor):
                    dados[col] = None
                elif hasattr(valor, "isoformat"):
                    dados[col] = valor.isoformat()
                else:
                    dados[col] = valor if isinstance(valor, (int, float)) else str(valor)

            item = models.ImportacaoItem(
                linha=linha_excel,
                codigo_produto_planilha=str(dados.get("produto") or ""),
                quantidade=None,
                valor=None,
                status="pendente_validacao",
                dados_json=json.dumps(dados, ensure_ascii=False, default=str),
                id_importacao=importacao.id,
            )
            self.importacao_repository.adicionar_item(item)

        self.db.commit()
        self.db.refresh(importacao)

        self.log_repository.registrar(
            tipo_operacao="importacao_planilha",
            resumo=f"Planilha '{filename}' importada com {len(df)} registros.",
            usuario_id=usuario.id,
            importacao_id=importacao.id,
        )

        return importacao

    def registrar_erro(self, filename: str, usuario, mensagem: str) -> None:
        importacao = models.Importacao(
            nome_arquivo=filename,
            status="erro",
            observacao=mensagem,
            id_usuario=usuario.id,
        )
        self.importacao_repository.salvar(importacao)

        self.log_repository.registrar(
            tipo_operacao="importacao_planilha",
            resumo=f"Falha ao importar '{filename}': {mensagem}",
            usuario_id=usuario.id,
            importacao_id=importacao.id,
        )
