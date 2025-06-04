from fastapi import APIRouter

setup_db_router = APIRouter(prefix="/admin", tags=["Utilitários"])

@setup_db_router.post("/setup-db")
def setup_db_route():
    return {"detail": "setup_db() ignorado, tabelas já criadas via SQLAlchemy."}
