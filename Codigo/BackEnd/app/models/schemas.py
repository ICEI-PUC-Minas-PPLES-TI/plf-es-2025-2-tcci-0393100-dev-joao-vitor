from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional, Literal

Role = Literal["administrador", "gestor", "analista", "vendedor", "executivo"]


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    nome: str
    email: EmailStr
    role: Role


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


class DashboardSummary(BaseModel):
    total_vendas: float
    total_pedidos: int
    ticket_medio: float
    meta_percentual: float


class ImportLogOut(BaseModel):
    id: int
    nome_arquivo: str
    usuario_id: int
    usuario_nome: str
    status: str
    created_at: datetime
    observacao: Optional[str] = None