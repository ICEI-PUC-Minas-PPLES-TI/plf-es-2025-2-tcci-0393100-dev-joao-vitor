# DashVendas — Código do Sistema

O sistema está dividido em dois módulos independentes:

```
Codigo/
├── BackEnd/    API REST em FastAPI + SQLAlchemy (SQLite em dev / PostgreSQL em produção)
└── Frontend/   SPA em React + Vite
```

---

## Back-end (`BackEnd/`)

API REST desenvolvida em **Python 3.11 + FastAPI**, com **SQLAlchemy** como ORM.
Concentra as regras de negócio, a autenticação (JWT), o processamento de
planilhas, o cálculo de indicadores e a integração com o assistente de IA.

**Executar:**
```bash
cd BackEnd
py -m venv .venv
.venv\Scripts\activate         # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload  # http://localhost:8000
```

Documentação interativa da API: `http://localhost:8000/docs`.

**Testes:**
```bash
pytest
```

---

## Front-end (`Frontend/`)

Aplicação **React 18 + Vite**, consumindo a API via **Axios**.

**Executar:**
```bash
cd Frontend
npm install
npm run dev                    # http://localhost:5173
```

---

## Configuração

O back-end lê as configurações de um arquivo `.env` em `BackEnd/`. Consulte o
[README principal](../README.md) para a lista de variáveis de ambiente, as
credenciais de teste e as instruções completas de instalação.
