from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.auth import Order as OrderModel, OrderItem as OrderItemModel, Product as ProductModel, Client
from app.auth import OrderCreate, OrderRead, OrderUpdate, OrderStatus as EnumStatus

order_router = APIRouter(prefix="/orders", tags=["orders"])

def apply_order_filters(query, client_id: Optional[int], status: Optional[EnumStatus],
                        start_date: Optional[datetime], end_date: Optional[datetime], section: Optional[str]):
    if client_id:
        query = query.filter(OrderModel.client_id == client_id)
    if status:
        query = query.filter(OrderModel.status == status)
    if start_date:
        query = query.filter(OrderModel.created_at >= start_date)
    if end_date:
        query = query.filter(OrderModel.created_at <= end_date)
    if section:

        query = query.join(OrderModel.items).join(OrderItemModel.product).filter(ProductModel.section == section)
    return query

@order_router.get("", response_model=List[OrderRead])
def list_orders(
    client_id: Optional[int] = Query(None),
    status: Optional[EnumStatus] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    section: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(OrderModel)
    query = apply_order_filters(query, client_id, status, start_date, end_date, section)
    orders = query.all()
    return orders

@order_router.post("/", response_model=OrderRead)
def create_order(
        order: OrderCreate,
        db: Session = Depends(get_db)
):
    db_client = db.get(Client, order.client_id)
    if not db_client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    db_order = OrderModel(client_id=order.client_id, status=EnumStatus.pending)
    db.add(db_order)
    db.flush()

    for item in order.items:
        db_product = db.get(ProductModel, item.product_id)
        if not db_product:
            raise HTTPException(status_code=404, detail=f"Produto com ID {item.product_id} não encontrado")

        if db_product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Estoque insuficiente para o produto {db_product.name}")

        db_product.stock -= item.quantity

        db_item = OrderItemModel(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=db_product.price
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_order)
    return db_order

@order_router.get("/{order_id}", response_model=OrderRead)
def get_order(
        order_id: int,
        db: Session = Depends(get_db)
):
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return order

@order_router.put("/{order_id}", response_model=OrderRead)
def update_order(
        order_id: int,
        order_update: OrderUpdate,
        db: Session = Depends(get_db)
):
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    update_data = order_update.dict(exclude_unset=True)

    if "status" in update_data:
        order.status = update_data["status"]

    if "items" in update_data:
        new_items = update_data["items"]

        product_ids = [item.product_id for item in new_items]
        if len(product_ids) != len(set(product_ids)):
            raise HTTPException(status_code=400, detail="Cada produto deve aparecer apenas uma vez no pedido")

        for item in order.items:
            product = db.query(ProductModel).filter(ProductModel.id == item.product_id).first()
            product.stock += item.quantity

        db.query(OrderItemModel).filter(OrderItemModel.order_id == order_id).delete()

        for item in new_items:
            product = db.query(ProductModel).filter(ProductModel.id == item.product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail=f"Produto {item.product_id} não encontrado")
            if product.stock < item.quantity:
                raise HTTPException(status_code=400, detail=f"Estoque insuficiente para o produto {product.description}")

            db_item = OrderItemModel(order_id=order.id, product_id=item.product_id, quantity=item.quantity)
            db.add(db_item)
            product.stock -= item.quantity

    db.commit()
    db.refresh(order)
    return order

@order_router.delete("/{order_id}", status_code=204)
def delete_order(
        order_id: int,
        db: Session = Depends(get_db)
):
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    for item in order.items:
        product = db.query(ProductModel).filter(ProductModel.id == item.product_id).first()
        product.stock += item.quantity

    db.query(OrderItemModel).filter(OrderItemModel.order_id == order_id).delete()
    db.delete(order)
    db.commit()
    return None
