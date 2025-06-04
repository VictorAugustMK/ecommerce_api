
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List

from app.auth import get_current_user
from app.db.session import get_db
from app.auth import Client as ClientModel
from app.auth import ClientRead, ClientCreate, ClientUpdate

client_router = APIRouter(prefix="/clients", tags=["clients"], dependencies=[Depends(get_current_user)])

@client_router.get("/", response_model=List[ClientRead], dependencies=[Depends(get_db)])
def list_clients(db: Session = Depends(get_db)):

    clients = db.query(ClientModel).all()
    return clients

@client_router.get("/{client_id}", response_model=ClientRead)
def get_client_by_id(
        client_id: int,
        db: Session = Depends(get_db)
):
    client = db.query(ClientModel).filter(ClientModel.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@client_router.post("/", response_model=ClientRead)
def create_client(
        client: ClientCreate,
        db: Session = Depends(get_db)
):
    if db.query(ClientModel).filter(ClientModel.email == client.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já está em uso"
        )

    if db.query(ClientModel).filter(ClientModel.cpf == client.cpf).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF já está em uso"
        )

    db_client = ClientModel(**client.dict())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@client_router.put("/{client_id}", response_model=ClientRead)
def update_client(
    client_id: int,
    client_update: ClientUpdate = Body(...),
    db: Session = Depends(get_db)
):
    db_client = db.query(ClientModel).filter(ClientModel.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")

    update_data = client_update.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Pelo menos um campo deve ser informado para atualização")

    for key, value in update_data.items():
        setattr(db_client, key, value)

    db.commit()
    db.refresh(db_client)
    return db_client

@client_router.delete("/{client_id}", status_code=204)
def delete_client(
        client_id: int,
        db: Session = Depends(get_db)
):
    db_client = db.query(ClientModel).filter(ClientModel.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")

    db.delete(db_client)
    db.commit()
    return