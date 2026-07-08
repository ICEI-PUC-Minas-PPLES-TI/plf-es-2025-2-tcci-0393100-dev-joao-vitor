"""Autenticação e autorização (JWT + perfis de acesso)."""

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.services.usuario_service import UsuarioService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        ) from exc


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Usuário inválido")

    user = UsuarioService(db).obter_por_id(int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    if user.ativo is False:
        raise HTTPException(status_code=403, detail="Usuário desativado")
    return user


def require_roles(*roles):
    def role_checker(current_user=Depends(get_current_user)):
        if current_user.tipo_usuario not in roles:
            raise HTTPException(status_code=403, detail="Acesso negado")
        return current_user

    return role_checker
