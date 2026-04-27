import io
import re
import unicodedata
from difflib import SequenceMatcher
from typing import Any

import pandas as pd


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


PRODUTOS_CADASTRADOS = [
    {"id": 1, "nome": "Notebook Dell", "categoria": "Informática"},
    {"id": 2, "nome": "Mouse Logitech", "categoria": "Periféricos"},
    {"id": 3, "nome": "Teclado Mecânico", "categoria": "Periféricos"},
    {"id": 4, "nome": "Monitor LG", "categoria": "Informática"},
    {"id": 5, "nome": "Cadeira Escritório", "categoria": "Móveis"},
]


def normalize_text(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""

    text = str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^a-z0-9_]", "", text)
    return text


def normalize_columns(columns):
    return [normalize_text(col) for col in columns]


def to_float(value: Any, field_name: str, errors: list[str]) -> float | None:
    if value is None or pd.isna(value) or value == "":
        errors.append(f"{field_name} ausente")
        return None

    try:
        number = float(value)
    except (TypeError, ValueError):
        errors.append(f"{field_name} inválido")
        return None

    if number <= 0:
        errors.append(f"{field_name} deve ser maior que zero")
        return None

    return number


def format_date(value: Any, errors: list[str]) -> str | None:
    if value is None or pd.isna(value) or value == "":
        errors.append("data_venda ausente")
        return None

    try:
        parsed_date = pd.to_datetime(value, dayfirst=True)
        return parsed_date.strftime("%Y-%m-%d")
    except Exception:
        errors.append("data_venda inválida")
        return None


def calcular_similaridade(texto_a: Any, texto_b: Any) -> float:
    texto_a = normalize_text(texto_a).replace("_", " ")
    texto_b = normalize_text(texto_b).replace("_", " ")

    if not texto_a or not texto_b:
        return 0.0

    return SequenceMatcher(None, texto_a, texto_b).ratio()


def cruzar_produto(nome_produto: str) -> dict:
    melhor_produto = None
    maior_score = 0.0

    for produto in PRODUTOS_CADASTRADOS:
        score = calcular_similaridade(nome_produto, produto["nome"])

        if score > maior_score:
            maior_score = score
            melhor_produto = produto

    if melhor_produto and maior_score >= 0.75:
        return {
            "produto_id": melhor_produto["id"],
            "produto_cadastrado": melhor_produto["nome"],
            "categoria_cadastrada": melhor_produto["categoria"],
            "confianca_cruzamento": round(maior_score, 2),
            "status_cruzamento": "encontrado",
        }

    return {
        "produto_id": None,
        "produto_cadastrado": None,
        "categoria_cadastrada": None,
        "confianca_cruzamento": round(maior_score, 2),
        "status_cruzamento": "nao_encontrado",
    }


def process_excel_file(file_bytes: bytes) -> dict:
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

    registros_validos = []
    registros_invalidos = []
    chaves_processadas = set()

    for idx, row in df.iterrows():
        linha_excel = idx + 2
        erros_linha = []

        data_venda = format_date(row["data_venda"], erros_linha)
        vendedor = str(row["vendedor"]).strip() if not pd.isna(row["vendedor"]) else ""
        regiao = str(row["regiao"]).strip() if not pd.isna(row["regiao"]) else ""
        produto = str(row["produto"]).strip() if not pd.isna(row["produto"]) else ""
        categoria = str(row["categoria"]).strip() if not pd.isna(row["categoria"]) else ""

        if not vendedor:
            erros_linha.append("vendedor ausente")
        if not regiao:
            erros_linha.append("regiao ausente")
        if not produto:
            erros_linha.append("produto ausente")
        if not categoria:
            erros_linha.append("categoria ausente")

        quantidade = to_float(row["quantidade"], "quantidade", erros_linha)
        valor_unitario = to_float(row["valor_unitario"], "valor_unitario", erros_linha)
        valor_total = to_float(row["valor_total"], "valor_total", erros_linha)

        chave = (
            data_venda,
            normalize_text(vendedor),
            normalize_text(produto),
            quantidade,
            valor_total,
        )

        if chave in chaves_processadas:
            erros_linha.append("registro duplicado")
        else:
            chaves_processadas.add(chave)

        if quantidade and valor_unitario and valor_total:
            valor_calculado = round(quantidade * valor_unitario, 2)
            if abs(valor_calculado - valor_total) > 0.05:
                erros_linha.append(
                    "valor_total incompatível com quantidade x valor_unitario"
                )

        if erros_linha:
            registros_invalidos.append({
                "linha": linha_excel,
                "produto": produto,
                "erros": erros_linha,
            })
            continue

        registro = {
            "data_venda": data_venda,
            "vendedor": vendedor,
            "regiao": regiao,
            "produto": produto,
            "categoria": categoria,
            "quantidade": quantidade,
            "valor_unitario": valor_unitario,
            "valor_total": valor_total,
        }

        registro.update(cruzar_produto(produto))
        registros_validos.append(registro)

    return {
        "total_registros": len(df),
        "total_validos": len(registros_validos),
        "total_invalidos": len(registros_invalidos),
        "registros": registros_validos,
        "registros_invalidos": registros_invalidos,
        "colunas": REQUIRED_COLUMNS,
        "resumo_validacao": {
            "cruzamento_produtos": True,
            "criterio_similaridade_minima": 0.75,
        },
    }