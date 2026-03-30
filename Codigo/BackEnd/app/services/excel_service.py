import io
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


def normalize_columns(columns):
    return [str(col).strip().lower() for col in columns]


def process_excel_file(file_bytes: bytes):
    try:
        df = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
    except Exception as exc:
        raise ValueError(f"Erro ao ler o arquivo Excel: {str(exc)}") from exc

    df.columns = normalize_columns(df.columns)

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(
            f"Colunas obrigatórias ausentes: {', '.join(missing_columns)}"
        )

    df = df[REQUIRED_COLUMNS].copy()

    df = df.dropna(how="all")

    errors = []

    for idx, row in df.iterrows():
        linha_excel = idx + 2

        if pd.isna(row["vendedor"]):
            errors.append(f"Linha {linha_excel}: vendedor ausente")

        if pd.isna(row["produto"]):
            errors.append(f"Linha {linha_excel}: produto ausente")

        if pd.isna(row["valor_total"]):
            errors.append(f"Linha {linha_excel}: valor_total ausente")

    if errors:
        raise ValueError(" ; ".join(errors[:10]))

    records = df.fillna("").to_dict(orient="records")

    for record in records:
        if hasattr(record["data_venda"], "strftime"):
            record["data_venda"] = record["data_venda"].strftime("%Y-%m-%d")

        for numeric_field in ["quantidade", "valor_unitario", "valor_total"]:
            try:
                record[numeric_field] = float(record[numeric_field])
            except Exception:
                record[numeric_field] = 0.0

    return {
        "total_registros": len(records),
        "registros": records,
        "colunas": REQUIRED_COLUMNS,
    }