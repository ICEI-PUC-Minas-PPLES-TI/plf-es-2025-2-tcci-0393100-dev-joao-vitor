from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth_routes import router as auth_router
from app.routes.dashboard_routes import router as dashboard_router
from app.routes.import_routes import router as import_router
from app.routes.kpi_routes import router as kpi_router
from app.routes.meta_routes import router as meta_router

app = FastAPI(title="DashVendas API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(import_router)
app.include_router(kpi_router)
app.include_router(meta_router)


@app.get("/")
def healthcheck():
    return {"status": "ok", "service": "DashVendas API"}