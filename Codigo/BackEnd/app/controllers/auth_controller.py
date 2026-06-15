

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import create_access_token
from app.db.database import get_db
from app.dtos.schemas import TokenResponseDTO, UserLoginDTO
from app.services.usuario_service import UsuarioService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponseDTO)
def login(payload: UserLoginDTO, db: Session = Depends(get_db)):
    usuario = UsuarioService(db).autenticar(payload.email, payload.password)
    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    access_token = create_access_token({"sub": str(usuario.id), "role": usuario.tipo_usuario})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "role": usuario.tipo_usuario,
            "ativo": usuario.ativo,
        },
    }
