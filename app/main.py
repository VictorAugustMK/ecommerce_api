import os
from fastapi import FastAPI

from app.utils.db.setup import wait_for_db  # Importa o wait_for_db da função externa
from app.db.session import engine
from app.db.base_class import Base

from app.routers import (
    auth_router, client_router, product_router, order_router,
    db_reset_bp, setup_db_router,
)

app = FastAPI(
    title="Lu Estilos API",
    version="1.0.0",
    openapi_tags=[
        {"name": "Auth", "description": "Rotas de autenticação"},
        {"name": "Clientes", "description": "CRUD de clientes"},
        {"name": "Produtos", "description": "CRUD de produtos"},
        {"name": "Pedidos", "description": "CRUD de pedidos"},
        {"name": "Utilitários", "description": "Reset e Setup do banco"},
    ]
)

@app.on_event("startup")
async def startup():
    print("Aguardando banco de dados...")
    wait_for_db()
    print("Inicializando banco de dados...")
    async with engine.begin() as conn:
        print("Criando tabelas...")
        await conn.run_sync(Base.metadata.create_all)
        print("Tabelas criadas com sucesso.")

app.include_router(auth_router)
app.include_router(db_reset_bp)
app.include_router(setup_db_router)
app.include_router(client_router)
app.include_router(product_router)
app.include_router(order_router)

@app.get("/")
def root():
    return {"message": "API está rodando!"}
