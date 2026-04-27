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
        add_import_log(filename, current_user["id"], current_user["nome"], "erro", "Extensão inválida")
        raise HTTPException(status_code=400, detail="Arquivo inválido. Envie Excel .xlsx ou .xls")

    content = await arquivo.read()

    if not content:
        add_import_log(filename, current_user["id"], current_user["nome"], "erro", "Arquivo vazio")
        raise HTTPException(status_code=400, detail="Arquivo vazio")

    try:
        result = process_excel_file(content)

        if result["total_validos"] > 0:
            replace_sales_data(result["registros"])

        status = "processado" if result["total_invalidos"] == 0 else "processado_com_alertas"

        log = add_import_log(
            nome_arquivo=filename,
            usuario_id=current_user["id"],
            usuario_nome=current_user["nome"],
            status=status,
            observacao=(
                f"{result['total_validos']} registros válidos; "
                f"{result['total_invalidos']} registros inválidos. "
                "Validação automática e cruzamento de produtos executados."
            ),
        )

        return {
            "message": "Upload, validação e cruzamento realizados com sucesso",
            "importacao": log,
            "total_registros": result["total_registros"],
            "total_validos": result["total_validos"],
            "total_invalidos": result["total_invalidos"],
            "registros_invalidos": result["registros_invalidos"],
            "resumo_validacao": result["resumo_validacao"],
            "colunas_processadas": result["colunas"],
        }

    except ValueError as exc:
        add_import_log(filename, current_user["id"], current_user["nome"], "erro", str(exc))
        raise HTTPException(status_code=400, detail=str(exc)) from exc