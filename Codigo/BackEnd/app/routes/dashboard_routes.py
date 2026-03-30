from fastapi import APIRouter, Depends
from app.core.auth import get_current_user, require_roles
import app.services.mock_db as mock_db

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def get_summary(current_user=Depends(get_current_user)):
    return {
        "usuario": {
            "id": current_user["id"],
            "nome": current_user["nome"],
            "role": current_user["role"],
        },
        "resumo": mock_db.mock_dashboard,
    }


@router.get("/users")
def get_users(current_user=Depends(require_roles("administrador"))):
    return mock_db.list_users()


@router.get("/imports")
def get_imports(current_user=Depends(get_current_user)):
    return mock_db.mock_import_logs