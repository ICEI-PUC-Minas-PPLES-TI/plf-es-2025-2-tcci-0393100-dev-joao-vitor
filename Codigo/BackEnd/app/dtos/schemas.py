"""Objetos de Transferência de Dados (DTOs).

Este módulo materializa os DTOs descritos no diagrama de arquitetura
(Figura 31 / diagrama de DTOs): IARequestDTO, IAResponseDTO,
KPIResponseDTO, RelatorioDTO e ImportacaoResultadoDTO, além dos
modelos de entrada/saída usados pelos controllers (autenticação,
usuários, metas e agendamentos).
"""

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, EmailStr, Field

Role = Literal["administrador", "gestor", "analista", "vendedor", "executivo"]


# ---------------------------------------------------------------------------
# Autenticação / Usuários
# ---------------------------------------------------------------------------

class UserLoginDTO(BaseModel):
    email: EmailStr
    password: str


class UserOutDTO(BaseModel):
    id: int
    nome: str
    email: EmailStr
    role: Role
    ativo: Optional[bool] = True


class TokenResponseDTO(BaseModel):
    access_token: str
    token_type: str
    user: UserOutDTO


class UsuarioCreateDTO(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    tipo_usuario: Role


class UsuarioUpdateDTO(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    tipo_usuario: Optional[Role] = None
    senha: Optional[str] = None
    ativo: Optional[bool] = None


# ---------------------------------------------------------------------------
# KPIs (KPIResponseDTO)
# ---------------------------------------------------------------------------

class KPIResumoDTO(BaseModel):
    total_vendas: float
    quantidade_total: float
    total_pedidos: int
    ticket_medio: float


class KPIResponseDTO(BaseModel):
    filtros: dict[str, Any]
    resumo: KPIResumoDTO
    por_regiao: list[dict[str, Any]]
    por_categoria: list[dict[str, Any]]
    por_vendedor: list[dict[str, Any]]
    total_registros_considerados: int


# ---------------------------------------------------------------------------
# Metas
# ---------------------------------------------------------------------------

class MetaCreateDTO(BaseModel):
    periodo_inicio: str
    periodo_fim: str
    regiao: Optional[str] = None
    categoria: Optional[str] = None
    valor_meta: float = Field(gt=0)
    descricao: Optional[str] = None


# ---------------------------------------------------------------------------
# Importação (ImportacaoResultadoDTO)
# ---------------------------------------------------------------------------

class ImportacaoResultadoDTO(BaseModel):
    importacao_id: int
    nome_arquivo: str
    status: str
    etapa: str
    total_registros: int = 0
    total_validos: int = 0
    total_invalidos: int = 0
    registros_invalidos: list[dict[str, Any]] = []
    registros_processados: list[dict[str, Any]] = []
    resumo: Optional[str] = None


# ---------------------------------------------------------------------------
# Relatórios (RelatorioDTO)
# ---------------------------------------------------------------------------

class RelatorioDTO(BaseModel):
    id: int
    tipo: str
    periodo: Optional[str] = None
    caminho_arquivo: Optional[str] = None
    data_geracao: datetime
    id_usuario_solicitante: Optional[int] = None
    id_agendamento: Optional[int] = None


class AgendamentoCreateDTO(BaseModel):
    periodicidade: str
    destinatarios: str
    filtros: Optional[str] = None


class AgendamentoStatusDTO(BaseModel):
    ativo: bool


# ---------------------------------------------------------------------------
# Assistente IA (IARequestDTO / IAResponseDTO)
# ---------------------------------------------------------------------------

class IARequestDTO(BaseModel):
    """Pergunta em linguagem natural (UC13 - consultarIA)."""

    pergunta: str


class IAAnaliseRequestDTO(BaseModel):
    """Filtros para análise interpretativa (UC12 - gerarAnaliseIA)."""

    periodo_inicio: Optional[str] = None
    periodo_fim: Optional[str] = None
    regiao: Optional[str] = None
    categoria: Optional[str] = None


class IAResponseDTO(BaseModel):
    resposta: str
    pergunta: Optional[str] = None
    contexto: dict[str, Any] = {}
    dados: Optional[dict[str, Any]] = None
    provedor: str = "local"
