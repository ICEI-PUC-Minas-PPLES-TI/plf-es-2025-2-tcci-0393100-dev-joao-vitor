import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SQLITE_PADRAO = f"sqlite:///{os.path.join(BASE_DIR, 'dashvendas.db')}"

# A URL de conexão é lida da variável de ambiente DATABASE_URL (definida
# no arquivo .env). Se não houver, ou se estiver vazia, usa o SQLite
# local como padrão.
#
#   - SQLite (local):  sqlite:///.../dashvendas.db
#   - PostgreSQL (ex. Neon):
#       postgresql://usuario:senha@host/banco?sslmode=require
#
# Observação: o Neon fornece a string começando com "postgresql://".
# O SQLAlchemy aceita esse formato diretamente com o driver psycopg2.
DATABASE_URL = os.getenv("DATABASE_URL", "").strip() or SQLITE_PADRAO

# O parâmetro check_same_thread é específico do SQLite e não deve ser
# enviado para outros bancos (PostgreSQL, MySQL, etc.).
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # pool_pre_ping evita erros de conexão ociosa com bancos na nuvem.
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
