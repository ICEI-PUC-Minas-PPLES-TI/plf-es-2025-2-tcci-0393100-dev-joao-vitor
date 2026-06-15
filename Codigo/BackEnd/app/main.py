from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.seed import seed
from app.controllers.auth_controller import router as auth_router
from app.controllers.dashboard_controller import router as dashboard_router
from app.controllers.importacao_controller import router as importacao_router
from app.controllers.kpi_controller import router as kpi_router
from app.controllers.meta_controller import router as meta_router
from app.controllers.alerta_controller import router as alerta_router
from app.controllers.relatorio_controller import router as relatorio_router
from app.controllers.ia_controller import router as ia_router
from app.controllers.usuario_controller import router as usuario_router
from app.controllers.log_controller import router as log_router

app = FastAPI(title="DashVendas API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    seed()


app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(importacao_router)
app.include_router(kpi_router)
app.include_router(meta_router)
app.include_router(alerta_router)
app.include_router(relatorio_router)
app.include_router(ia_router)
app.include_router(usuario_router)
app.include_router(log_router)


@app.get("/")
def healthcheck():
    return {"status": "ok", "service": "DashVendas API"}
