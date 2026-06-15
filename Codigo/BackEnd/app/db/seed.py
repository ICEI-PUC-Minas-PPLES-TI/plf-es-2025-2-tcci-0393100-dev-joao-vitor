from passlib.context import CryptContext

from app.db.database import Base, engine, SessionLocal
from app.db import models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Regiões de referência do Brasil. São apenas rótulos geográficos
# neutros (não são dados de negócio) e servem de apoio aos filtros e
# relatórios. As vendas reais são consolidadas durante a importação.
REGIOES = [
    {"nome": "Sudeste", "codigo": "SE"},
    {"nome": "Sul", "codigo": "S"},
    {"nome": "Nordeste", "codigo": "NE"},
    {"nome": "Centro-Oeste", "codigo": "CO"},
    {"nome": "Norte", "codigo": "N"},
]

# Usuários iniciais de acesso ao sistema. São necessários para o
# primeiro login, já que novos usuários só podem ser criados por um
# administrador autenticado (UC14). A senha padrão deve ser alterada
# após o primeiro acesso em ambiente real.
#
# Os dois vendedores (José e Laísa) têm nome próprio para que a tela
# "Meu Desempenho" (UC01) exiba dados individuais: as vendas importadas
# são distribuídas entre eles pelo conversor da base real.
USUARIOS = [
    {
        "nome": "Administrador",
        "email": "admin@dashvendas.com",
        "senha": "123456",
        "tipo_usuario": "administrador",
    },
    {
        "nome": "Gestor Comercial",
        "email": "gestor@dashvendas.com",
        "senha": "123456",
        "tipo_usuario": "gestor",
    },
    {
        "nome": "Analista de Dados",
        "email": "analista@dashvendas.com",
        "senha": "123456",
        "tipo_usuario": "analista",
    },
    {
        "nome": "José",
        "email": "jose@dashvendas.com",
        "senha": "123456",
        "tipo_usuario": "vendedor",
    },
    {
        "nome": "Laísa",
        "email": "laisa@dashvendas.com",
        "senha": "123456",
        "tipo_usuario": "vendedor",
    },
    {
        "nome": "Diretor Executivo",
        "email": "executivo@dashvendas.com",
        "senha": "123456",
        "tipo_usuario": "executivo",
    },
]


def seed():
    """Popula o banco com os dados mínimos para o primeiro uso.

    Cria apenas usuários de acesso e as regiões de referência. NÃO
    cadastra produtos nem vendas: o catálogo de produtos e as vendas vêm
    dos dados reais (carga do catálogo + importação de planilhas).
    Executa somente uma vez, quando o banco está vazio.
    """

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(models.Usuario).count() > 0:
            return  # banco já populado

        for r in REGIOES:
            db.add(models.Regiao(**r))

        for u in USUARIOS:
            db.add(models.Usuario(
                nome=u["nome"],
                email=u["email"],
                senha_hash=hash_password(u["senha"]),
                tipo_usuario=u["tipo_usuario"],
            ))

        db.commit()
    finally:
        db.close()
