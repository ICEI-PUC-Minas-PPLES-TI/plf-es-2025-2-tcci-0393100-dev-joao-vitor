"""Configuração compartilhada dos testes (pytest fixtures).

Cria um banco SQLite em memória isolado por teste e popula o catálogo
de produtos, as regiões e um usuário analista, reproduzindo as
pré-condições descritas nos casos de teste da Seção 6 da documentação.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.db import models


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    produtos = [
        {"codigo_interno": "P001", "descricao": "Notebook Dell", "categoria": "Informática"},
        {"codigo_interno": "P002", "descricao": "Mouse Logitech", "categoria": "Periféricos"},
        {"codigo_interno": "P003", "descricao": "Teclado Mecânico", "categoria": "Periféricos"},
        {"codigo_interno": "P004", "descricao": "Monitor LG", "categoria": "Informática"},
        {"codigo_interno": "P005", "descricao": "Cadeira Escritório", "categoria": "Móveis"},
    ]
    for p in produtos:
        session.add(models.Produto(**p))

    regioes = ["Sudeste", "Sul", "Nordeste", "Norte", "Centro-Oeste"]
    for nome in regioes:
        session.add(models.Regiao(nome=nome, codigo=nome[:3].upper()))

    usuario = models.Usuario(
        nome="Analista Teste",
        email="teste@dashvendas.com",
        senha_hash="x",
        tipo_usuario="analista",
    )
    session.add(usuario)
    session.commit()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def usuario(db_session):
    return db_session.query(models.Usuario).first()
