from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.schemas.product import (ProductCreate,ProductResponse)
from app.utils.dependencies import get_current_user
from app.schemas.product import SellerDashboardResponse
from app.models.order import Order
from app.models.order_item import OrderItem


router = APIRouter(prefix="/seller",tags=["Seller"])

@router.post(
    "/products",
    response_model=ProductResponse
)
def add_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "seller":
        raise HTTPException(
            status_code=403,
            detail="Seller access required"
        )


    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        image=product.image,
        seller_id=current_user.id
    )


    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product



@router.get(
    "/products",
    response_model=list[ProductResponse]
)
def get_seller_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "seller":
        raise HTTPException(
            status_code=403,
            detail="Seller access required"
        )


    products = db.query(Product).filter(
        Product.seller_id == current_user.id
    ).all()
    return products

@router.get(
    "/dashboard",
    response_model=SellerDashboardResponse
)


def seller_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "seller":
        raise HTTPException(
            status_code=403,
            detail="Seller access required"
        )


    products = db.query(Product).filter(
        Product.seller_id == current_user.id
    ).all()


    recent_products = db.query(Product).filter(
        Product.seller_id == current_user.id
    ).order_by(
        Product.id.desc()
    ).limit(5).all()



    seller_orders = (
        db.query(
            Order,
            OrderItem,
            Product
        )
        .join(
            OrderItem,
            Order.id == OrderItem.order_id
        )
        .join(
            Product,
            OrderItem.product_id == Product.id
        )
        .filter(
            Product.seller_id == current_user.id
        )
        .all()
    )


    order_ids = {
        order.id
        for order, order_item, product
        in seller_orders
    }


    customer_ids = {
        order.customer_id
        for order, order_item, product
        in seller_orders
    }


    total_revenue = sum(
        order_item.price * order_item.quantity
        for order, order_item, product
        in seller_orders
    )


    return {
        "seller_name": current_user.full_name,
        "total_products": len(products),
        "total_orders": len(order_ids),
        "total_revenue": total_revenue,
        "total_customers": len(customer_ids),
        "recent_products": recent_products
    }