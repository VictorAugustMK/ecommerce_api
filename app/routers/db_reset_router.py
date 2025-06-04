from fastapi import APIRouter
from app.utils.db.reset import reset_database

db_reset_bp = APIRouter()

@db_reset_bp.post("/reset-db")
def reset_db_route():
    reset_database()
    return {"detail": "Banco de dados resetado com sucesso."}
