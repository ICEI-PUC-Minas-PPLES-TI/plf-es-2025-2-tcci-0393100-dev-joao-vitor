from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


mock_users = [
    {
        "id": 1,
        "nome": "Admin DashVendas",
        "email": "admin@dashvendas.com",
        "password_hash": hash_password("123456"),
        "role": "administrador",
    },
    {
        "id": 2,
        "nome": "Gestor Comercial",
        "email": "gestor@dashvendas.com",
        "password_hash": hash_password("123456"),
        "role": "gestor",
    },
    {
        "id": 3,
        "nome": "Analista de Dados",
        "email": "analista@dashvendas.com",
        "password_hash": hash_password("123456"),
        "role": "analista",
    },
]

mock_import_logs = []
mock_sales_data = []

mock_dashboard = {
    "total_vendas": 0.0,
    "total_pedidos": 0,
    "ticket_medio": 0.0,
    "meta_percentual": 0.0,
}


def get_user_by_email(email: str):
    return next((u for u in mock_users if u["email"] == email), None)


def get_user_by_id(user_id: int):
    return next((u for u in mock_users if u["id"] == user_id), None)


def list_users():
    return [
        {"id": u["id"], "nome": u["nome"], "email": u["email"], "role": u["role"]}
        for u in mock_users
    ]


def add_import_log(nome_arquivo: str, usuario_id: int, usuario_nome: str, status: str, observacao: str | None = None):
    new_id = len(mock_import_logs) + 1
    log = {
        "id": new_id,
        "nome_arquivo": nome_arquivo,
        "usuario_id": usuario_id,
        "usuario_nome": usuario_nome,
        "status": status,
        "created_at": datetime.utcnow(),
        "observacao": observacao,
    }
    mock_import_logs.insert(0, log)
    return log


def replace_sales_data(new_rows: list[dict]):
    global mock_sales_data
    mock_sales_data = new_rows
    recalculate_dashboard()


def recalculate_dashboard():
    total_vendas = sum(float(row.get("valor_total", 0) or 0) for row in mock_sales_data)
    total_pedidos = len(mock_sales_data)
    ticket_medio = total_vendas / total_pedidos if total_pedidos > 0 else 0.0

    mock_dashboard["total_vendas"] = round(total_vendas, 2)
    mock_dashboard["total_pedidos"] = total_pedidos
    mock_dashboard["ticket_medio"] = round(ticket_medio, 2)
    mock_dashboard["meta_percentual"] = 82.0 if total_pedidos > 0 else 0.0