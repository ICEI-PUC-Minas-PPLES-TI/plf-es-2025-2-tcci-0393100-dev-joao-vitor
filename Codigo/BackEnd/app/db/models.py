from datetime import datetime, date

from sqlalchemy import (
    Text,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.db.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False, unique=True, index=True)
    senha_hash = Column(String(255), nullable=False)
    tipo_usuario = Column(String(30), nullable=False)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    ativo = Column(Boolean, default=True)

    metas = relationship("Meta", back_populates="usuario_responsavel")
    importacoes = relationship("Importacao", back_populates="usuario")
    agendamentos = relationship("AgendamentoRelatorio", back_populates="usuario_criador")
    relatorios = relationship("Relatorio", back_populates="usuario_solicitante")


class Regiao(Base):
    __tablename__ = "regioes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False, unique=True)
    codigo = Column(String(50), nullable=False)

    vendas = relationship("Venda", back_populates="regiao")


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    codigo_interno = Column(String(100), nullable=False)
    # Campos de texto livre vindos da base real usam Text (sem limite),
    # evitando erros de tamanho no PostgreSQL.
    descricao = Column(Text, nullable=False)
    categoria = Column(String(150), nullable=False)

    vendas = relationship("Venda", back_populates="produto")


class Venda(Base):
    __tablename__ = "vendas"

    id = Column(Integer, primary_key=True, index=True)
    data_venda = Column(Date, nullable=False)
    quantidade = Column(Float, nullable=False)
    valor_total = Column(Float, nullable=False)

    vendedor_nome = Column(String(150), nullable=False)
    regiao_nome = Column(String(150), nullable=False)
    # Nome do produto e categoria vindos da planilha real podem ser
    # longos; Text evita qualquer limite.
    produto_nome = Column(Text, nullable=False)
    categoria_nome = Column(Text, nullable=False)

    id_regiao = Column(Integer, ForeignKey("regioes.id"), nullable=True)
    id_produto = Column(Integer, ForeignKey("produtos.id"), nullable=True)

    regiao = relationship("Regiao", back_populates="vendas")
    produto = relationship("Produto", back_populates="vendas")


class Meta(Base):
    __tablename__ = "metas"

    id = Column(Integer, primary_key=True, index=True)
    # Campos de período podem conter intervalos textuais (ex.:
    # "2025-01-01 a 2025-12-31"); Text evita limite de tamanho.
    periodo_inicio = Column(Text, nullable=False)
    periodo_fim = Column(Text, nullable=False)
    regiao = Column(String(150), nullable=True)
    categoria = Column(Text, nullable=True)
    valor_meta = Column(Float, nullable=False)
    descricao = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    id_usuario_responsavel = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    usuario_responsavel = relationship("Usuario", back_populates="metas")

    kpis = relationship("KPI", back_populates="meta")


class KPI(Base):
    __tablename__ = "kpis"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    valor = Column(Float, nullable=False)
    periodo = Column(Text, nullable=True)

    id_meta = Column(Integer, ForeignKey("metas.id"), nullable=True)
    id_regiao = Column(Integer, ForeignKey("regioes.id"), nullable=True)

    meta = relationship("Meta", back_populates="kpis")
    alertas = relationship("Alerta", back_populates="kpi")


class Alerta(Base):
    __tablename__ = "alertas"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(50), nullable=False)
    mensagem = Column(Text, nullable=False)
    nivel_criticidade = Column(String(30), nullable=False)
    periodo_referencia = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    lido = Column(Boolean, default=False)

    id_kpi = Column(Integer, ForeignKey("kpis.id"), nullable=True)
    kpi = relationship("KPI", back_populates="alertas")


class Importacao(Base):
    __tablename__ = "importacoes"

    id = Column(Integer, primary_key=True, index=True)
    data_importacao = Column(DateTime, default=datetime.utcnow)
    nome_arquivo = Column(String(255), nullable=False)
    status = Column(String(30), nullable=False)
    observacao = Column(Text, nullable=True)

    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    usuario = relationship("Usuario", back_populates="importacoes")

    itens = relationship("ImportacaoItem", back_populates="importacao")
    logs = relationship("LogImportacao", back_populates="importacao")


class ImportacaoItem(Base):
    __tablename__ = "importacao_itens"

    id = Column(Integer, primary_key=True, index=True)
    linha = Column(Integer, nullable=False)
    # Código/descrição do produto vindo da planilha real pode ser longo.
    codigo_produto_planilha = Column(Text, nullable=True)
    quantidade = Column(Float, nullable=True)
    valor = Column(Float, nullable=True)
    status = Column(String(30), nullable=False)
    mensagem_erro = Column(Text, nullable=True)

    # Dados brutos da linha, preservados entre as etapas de
    # importação (UC08), validação (UC09) e cruzamento (UC10).
    dados_json = Column(Text, nullable=True)

    # Resultado do cruzamento automático de produtos (UC10)
    confianca_cruzamento = Column(Float, nullable=True)
    status_cruzamento = Column(String(30), nullable=True)

    id_importacao = Column(Integer, ForeignKey("importacoes.id"), nullable=False)
    id_produto = Column(Integer, ForeignKey("produtos.id"), nullable=True)

    importacao = relationship("Importacao", back_populates="itens")


class LogImportacao(Base):
    __tablename__ = "logs_importacao"

    id = Column(Integer, primary_key=True, index=True)
    data_hora = Column(DateTime, default=datetime.utcnow)
    tipo_operacao = Column(String(50), nullable=False)
    resumo = Column(Text, nullable=True)

    id_importacao = Column(Integer, ForeignKey("importacoes.id"), nullable=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    importacao = relationship("Importacao", back_populates="logs")


class AgendamentoRelatorio(Base):
    __tablename__ = "agendamentos_relatorio"

    id = Column(Integer, primary_key=True, index=True)
    periodicidade = Column(String(50), nullable=False)
    destinatarios = Column(Text, nullable=False)
    filtros = Column(Text, nullable=True)
    ativo = Column(Boolean, default=True)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    ultimo_envio = Column(DateTime, nullable=True)

    id_usuario_criador = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    usuario_criador = relationship("Usuario", back_populates="agendamentos")

    relatorios = relationship("Relatorio", back_populates="agendamento")


class Relatorio(Base):
    __tablename__ = "relatorios"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(50), nullable=False)
    periodo = Column(Text, nullable=True)
    caminho_arquivo = Column(String(255), nullable=True)
    data_geracao = Column(DateTime, default=datetime.utcnow)

    id_usuario_solicitante = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    usuario_solicitante = relationship("Usuario", back_populates="relatorios")

    id_agendamento = Column(Integer, ForeignKey("agendamentos_relatorio.id"), nullable=True)
    agendamento = relationship("AgendamentoRelatorio", back_populates="relatorios")
