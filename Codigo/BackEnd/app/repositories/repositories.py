"""Camada de Repositórios (padrão Repository).

Materializa os repositórios descritos no diagrama de arquitetura:
UsuarioRepository, VendaRepository, ProdutoRepository, RegiaoRepository,
MetaRepository, KPIRepository, AlertaRepository, ImportacaoRepository,
LogRepository, RelatorioRepository e AgendamentoRepository.

Cada repositório encapsula o acesso ao banco de dados, isolando os
detalhes de persistência da camada de serviços (baixo acoplamento e
maior testabilidade, conforme Seção 3.4 da documentação).
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.db import models


class BaseRepository:
    def __init__(self, db: Session):
        self.db = db


class UsuarioRepository(BaseRepository):
    def obter_por_email(self, email: str) -> Optional[models.Usuario]:
        return self.db.query(models.Usuario).filter(models.Usuario.email == email).first()

    def obter_por_id(self, usuario_id: int) -> Optional[models.Usuario]:
        return self.db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()

    def listar(self) -> list[models.Usuario]:
        return self.db.query(models.Usuario).order_by(models.Usuario.id).all()

    def salvar(self, usuario: models.Usuario) -> models.Usuario:
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def remover(self, usuario: models.Usuario) -> None:
        self.db.delete(usuario)
        self.db.commit()


class RegiaoRepository(BaseRepository):
    def listar(self) -> list[models.Regiao]:
        return self.db.query(models.Regiao).all()

    def obter_por_nome(self, nome: str) -> Optional[models.Regiao]:
        return self.db.query(models.Regiao).filter(models.Regiao.nome.ilike(nome)).first()

    def obter_ou_criar(self, nome: str) -> Optional[models.Regiao]:
        if not nome:
            return None
        regiao = self.obter_por_nome(nome)
        if not regiao:
            regiao = models.Regiao(nome=nome, codigo=nome[:3].upper())
            self.db.add(regiao)
            self.db.flush()
        return regiao


class ProdutoRepository(BaseRepository):
    def listar(self) -> list[models.Produto]:
        return self.db.query(models.Produto).all()

    def listar_categorias(self) -> set[str]:
        return {p.categoria for p in self.listar()}


class VendaRepository(BaseRepository):
    def consultar(
        self,
        periodo_inicio=None,
        periodo_fim=None,
        regiao: Optional[str] = None,
        categoria: Optional[str] = None,
        vendedor: Optional[str] = None,
    ) -> list[models.Venda]:
        query = self.db.query(models.Venda)

        if periodo_inicio:
            query = query.filter(models.Venda.data_venda >= periodo_inicio)
        if periodo_fim:
            query = query.filter(models.Venda.data_venda <= periodo_fim)
        if regiao:
            query = query.filter(models.Venda.regiao_nome.ilike(regiao))
        if categoria:
            query = query.filter(models.Venda.categoria_nome.ilike(categoria))
        if vendedor:
            query = query.filter(models.Venda.vendedor_nome.ilike(vendedor))

        return query.all()

    def adicionar(self, venda: models.Venda) -> None:
        self.db.add(venda)


class MetaRepository(BaseRepository):
    def listar(self) -> list[models.Meta]:
        return self.db.query(models.Meta).order_by(models.Meta.id.desc()).all()

    def obter_por_id(self, meta_id: int) -> Optional[models.Meta]:
        return self.db.query(models.Meta).filter(models.Meta.id == meta_id).first()

    def salvar(self, meta: models.Meta) -> models.Meta:
        self.db.add(meta)
        self.db.commit()
        self.db.refresh(meta)
        return meta

    def remover(self, meta: models.Meta) -> None:
        self.db.delete(meta)
        self.db.commit()


class KPIRepository(BaseRepository):
    def salvar(self, kpi: models.KPI) -> models.KPI:
        self.db.add(kpi)
        self.db.commit()
        self.db.refresh(kpi)
        return kpi

    def listar(self) -> list[models.KPI]:
        return self.db.query(models.KPI).order_by(models.KPI.id.desc()).all()


class AlertaRepository(BaseRepository):
    def listar(self, apenas_nao_lidos: bool = False) -> list[models.Alerta]:
        query = self.db.query(models.Alerta).order_by(models.Alerta.id.desc())
        if apenas_nao_lidos:
            query = query.filter(models.Alerta.lido.is_(False))
        return query.all()

    def obter_por_id(self, alerta_id: int) -> Optional[models.Alerta]:
        return self.db.query(models.Alerta).filter(models.Alerta.id == alerta_id).first()

    def existe_alerta(self, tipo: str, periodo_referencia: str, mensagem: str) -> bool:
        return (
            self.db.query(models.Alerta)
            .filter(
                models.Alerta.tipo == tipo,
                models.Alerta.periodo_referencia == periodo_referencia,
                models.Alerta.mensagem == mensagem,
            )
            .first()
            is not None
        )

    def adicionar(self, alerta: models.Alerta) -> None:
        self.db.add(alerta)

    def commit(self) -> None:
        self.db.commit()


class ImportacaoRepository(BaseRepository):
    def obter_por_id(self, importacao_id: int) -> Optional[models.Importacao]:
        return (
            self.db.query(models.Importacao)
            .filter(models.Importacao.id == importacao_id)
            .first()
        )

    def listar(self) -> list[models.Importacao]:
        return self.db.query(models.Importacao).order_by(models.Importacao.id.desc()).all()

    def salvar(self, importacao: models.Importacao) -> models.Importacao:
        self.db.add(importacao)
        self.db.commit()
        self.db.refresh(importacao)
        return importacao

    def listar_itens(self, importacao_id: int) -> list[models.ImportacaoItem]:
        return (
            self.db.query(models.ImportacaoItem)
            .filter(models.ImportacaoItem.id_importacao == importacao_id)
            .order_by(models.ImportacaoItem.linha)
            .all()
        )

    def adicionar_item(self, item: models.ImportacaoItem) -> None:
        self.db.add(item)

    def commit(self) -> None:
        self.db.commit()


class LogRepository(BaseRepository):
    """Repositório de logs de auditoria (US06 / US13).

    Registra operações críticas: importações, validações, cruzamentos,
    geração e envio de relatórios e alterações de usuários/permissões.
    """

    def registrar(
        self,
        tipo_operacao: str,
        resumo: str,
        usuario_id: Optional[int] = None,
        importacao_id: Optional[int] = None,
    ) -> models.LogImportacao:
        log = models.LogImportacao(
            data_hora=datetime.utcnow(),
            tipo_operacao=tipo_operacao,
            resumo=resumo,
            id_usuario=usuario_id,
            id_importacao=importacao_id,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def listar(self, tipo_operacao: Optional[str] = None) -> list[models.LogImportacao]:
        query = self.db.query(models.LogImportacao).order_by(models.LogImportacao.id.desc())
        if tipo_operacao:
            query = query.filter(models.LogImportacao.tipo_operacao == tipo_operacao)
        return query.all()


class RelatorioRepository(BaseRepository):
    def salvar(self, relatorio: models.Relatorio) -> models.Relatorio:
        self.db.add(relatorio)
        self.db.commit()
        self.db.refresh(relatorio)
        return relatorio

    def listar(self) -> list[models.Relatorio]:
        return self.db.query(models.Relatorio).order_by(models.Relatorio.id.desc()).all()

    def obter_por_id(self, relatorio_id: int) -> Optional[models.Relatorio]:
        return (
            self.db.query(models.Relatorio)
            .filter(models.Relatorio.id == relatorio_id)
            .first()
        )


class AgendamentoRepository(BaseRepository):
    def salvar(self, agendamento: models.AgendamentoRelatorio) -> models.AgendamentoRelatorio:
        self.db.add(agendamento)
        self.db.commit()
        self.db.refresh(agendamento)
        return agendamento

    def listar(self) -> list[models.AgendamentoRelatorio]:
        return (
            self.db.query(models.AgendamentoRelatorio)
            .order_by(models.AgendamentoRelatorio.id.desc())
            .all()
        )

    def listar_ativos(self) -> list[models.AgendamentoRelatorio]:
        return (
            self.db.query(models.AgendamentoRelatorio)
            .filter(models.AgendamentoRelatorio.ativo.is_(True))
            .all()
        )

    def obter_por_id(self, agendamento_id: int) -> Optional[models.AgendamentoRelatorio]:
        return (
            self.db.query(models.AgendamentoRelatorio)
            .filter(models.AgendamentoRelatorio.id == agendamento_id)
            .first()
        )

    def remover(self, agendamento: models.AgendamentoRelatorio) -> None:
        self.db.delete(agendamento)
        self.db.commit()
