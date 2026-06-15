
import json

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, require_roles
from app.db.database import get_db
from app.repositories.repositories import ImportacaoRepository, UsuarioRepository
from app.services.cruzamento_produto_service import CruzamentoProdutoService
from app.services.importacao_service import ImportacaoService
from app.services.validacao_planilha_service import ValidacaoPlanilhaService

router = APIRouter(prefix="/imports", tags=["Imports"])

ALLOWED_EXTENSIONS = (".xlsx", ".xls")


def _serializar_importacao(importacao, db: Session):
    usuario = UsuarioRepository(db).obter_por_id(importacao.id_usuario) if importacao.id_usuario else None
    return {
        "id": importacao.id,
        "nome_arquivo": importacao.nome_arquivo,
        "usuario_id": importacao.id_usuario,
        "usuario_nome": usuario.nome if usuario else "Desconhecido",
        "status": importacao.status,
        "created_at": importacao.data_importacao,
        "observacao": importacao.observacao,
    }


@router.post("/upload")
async def importar_planilha(
    arquivo: UploadFile = File(...),
    current_user=Depends(require_roles("analista", "administrador")),
    db: Session = Depends(get_db),
):
    """CO09 — importarPlanilha(arquivoExcel) (UC08)."""

    filename = arquivo.filename or "arquivo_sem_nome"
    service = ImportacaoService(db)

    if not filename.lower().endswith(ALLOWED_EXTENSIONS):
        service.registrar_erro(filename, current_user, "Extensão inválida")
        raise HTTPException(status_code=400, detail="Arquivo inválido. Envie Excel .xlsx ou .xls")

    content = await arquivo.read()

    if not content:
        service.registrar_erro(filename, current_user, "Arquivo vazio")
        raise HTTPException(status_code=400, detail="Arquivo vazio")

    try:
        importacao = service.importar_planilha(content, filename, current_user)
    except ValueError as exc:
        service.registrar_erro(filename, current_user, str(exc))
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    total_itens = len(ImportacaoRepository(db).listar_itens(importacao.id))

    return {
        "message": "Planilha importada com sucesso. Prossiga com a validação.",
        "importacao": _serializar_importacao(importacao, db),
        "etapa": "importacao",
        "total_registros": total_itens,
    }


@router.post("/{importacao_id}/validar")
def validar_planilha(
    importacao_id: int,
    current_user=Depends(require_roles("analista", "administrador")),
    db: Session = Depends(get_db),
):
    """CO10 — validarPlanilha(idPlanilha) (UC09)."""

    try:
        resultado = ValidacaoPlanilhaService(db).validar_planilha(importacao_id, current_user)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "message": "Validação concluída.",
        "importacao": _serializar_importacao(resultado["importacao"], db),
        "etapa": "validacao",
        "total_registros": resultado["total_registros"],
        "total_validos": resultado["total_validos"],
        "total_invalidos": resultado["total_invalidos"],
        "registros_invalidos": resultado["registros_invalidos"],
        "resumo": resultado["resumo"],
    }


@router.post("/{importacao_id}/cruzar")
def cruzar_produtos(
    importacao_id: int,
    current_user=Depends(require_roles("analista", "administrador")),
    db: Session = Depends(get_db),
):
    """CO11 — executarCruzamentoProdutos(idPlanilha) (UC10)."""

    try:
        resultado = CruzamentoProdutoService(db).cruzar_produtos(importacao_id, current_user)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "message": "Cruzamento de produtos concluído. Vendas consolidadas.",
        "importacao": _serializar_importacao(resultado["importacao"], db),
        "etapa": "cruzamento",
        "total_itens": resultado["total_itens"],
        "encontrados": resultado["encontrados"],
        "nao_encontrados": resultado["nao_encontrados"],
        "criterio_similaridade_minima": resultado["criterio_similaridade_minima"],
        "registros_processados": resultado["registros_processados"],
        "resumo": resultado["resumo"],
    }


@router.get("")
def listar_importacoes(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    importacoes = ImportacaoRepository(db).listar()
    return [_serializar_importacao(i, db) for i in importacoes]


@router.get("/{importacao_id}/itens")
def listar_itens_importacao(
    importacao_id: int,
    current_user=Depends(require_roles("analista", "administrador")),
    db: Session = Depends(get_db),
):
    itens = ImportacaoRepository(db).listar_itens(importacao_id)

    return [
        {
            "id": item.id,
            "linha": item.linha,
            "produto": item.codigo_produto_planilha,
            "quantidade": item.quantidade,
            "valor": item.valor,
            "status": item.status,
            "mensagem_erro": item.mensagem_erro,
            "status_cruzamento": item.status_cruzamento,
            "confianca_cruzamento": item.confianca_cruzamento,
            "dados": json.loads(item.dados_json) if item.dados_json else None,
        }
        for item in itens
    ]
