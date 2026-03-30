from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.core.auth import require_roles
from app.services.mock_db import add_import_log, replace_sales_data
from app.services.excel_service import process_excel_file

router = APIRouter(prefix="/imports", tags=["Imports"])

ALLOWED_EXTENSIONS = (".xlsx", ".xls")


@router.post("/upload")
async def upload_excel(
    arquivo: UploadFile = File(...),
    current_user=Depends(require_roles("analista", "administrador")),
):
    filename = arquivo.filename or "arquivo_sem_nome"

    if not filename.lower().endswith(ALLOWED_EXTENSIONS):
        add_import_log(
            nome_arquivo=filename,
            usuario_id=current_user["id"],
            usuario_nome=current_user["nome"],
            status="erro",
            observacao="Extensão inválida. Envie arquivo .xlsx ou .xls",
        )
        raise HTTPException(status_code=400, detail="Arquivo inválido. Envie Excel .xlsx ou .xls")

    content = await arquivo.read()
    if not content:
        raise HTTPException(status_code=400, detail="Arquivo vazio")

    try:
        result = process_excel_file(content)

        replace_sales_data(result["registros"])

        log = add_import_log(
            nome_arquivo=filename,
            usuario_id=current_user["id"],
            usuario_nome=current_user["nome"],
            status="processado",
            observacao=f"{result['total_registros']} registros importados com sucesso",
        )

        return {
            "message": "Upload e processamento realizados com sucesso",
            "importacao": log,
            "total_registros": result["total_registros"],
            "colunas_processadas": result["colunas"],
        }

    except ValueError as exc:
        log = add_import_log(
            nome_arquivo=filename,
            usuario_id=current_user["id"],
            usuario_nome=current_user["nome"],
            status="erro",
            observacao=str(exc),
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc