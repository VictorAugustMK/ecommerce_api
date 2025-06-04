
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.auth import get_current_user, admin_required
from app.db.session import get_db
from app.auth import Product as ProductModel
from app.auth import ProductRead, ProductCreate, ProductUpdate, UserRead

product_router = APIRouter(prefix="/products", tags=["products"], dependencies=[Depends(get_current_user)])

@product_router.get("/", response_model=List[ProductRead], dependencies=[Depends(get_db)])
def list_products(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    available: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(ProductModel)
    if category:
        query = query.filter(ProductModel.section == category)
    if min_price is not None:
        query = query.filter(ProductModel.price >= min_price)
    if max_price is not None:
        query = query.filter(ProductModel.price <= max_price)
    if available is not None:
        query = query.filter(ProductModel.available == available)

    return query.offset(skip).limit(limit).all()

@product_router.post("/", response_model=ProductRead)
def create_product(
        product: ProductCreate,
        db: Session = Depends(get_db),
        _user: UserRead = Depends(admin_required)
):
    db_product = ProductModel(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@product_router.get("/{product_id}", response_model=ProductRead)
def get_product(
        product_id: int,
        db: Session =
        Depends(get_db)
):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@product_router.put("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db)
):
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = product_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)
    return db_product

@product_router.delete("/{product_id}")
def delete_product(
        product_id: int,
        db: Session = Depends(get_db),
        _user: UserRead = Depends(admin_required)):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return {"detail": "Product deleted successfully"}
