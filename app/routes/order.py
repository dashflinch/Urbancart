from fastapi import (APIRouter,Depends,HTTPException,)
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem
from app.schemas.order import (CustomerOrderResponse, OrderCreate,SellerOrderResponse,)
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


@router.post("")
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "customer":
        raise HTTPException(
            status_code=403,
            detail="Customer access required"
        )


    total_amount = 0
    order_products = []


    for item in order.items:
        product = db.query(Product).filter(
            Product.id == item.product_id
        ).first()


        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )


        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for {product.name}"
            )


        total_amount += (product.price * item.quantity)

        order_products.append(
            (
                product,
                item.quantity
            )
        )

    new_order = Order(
        customer_id=current_user.id,
        total_amount=total_amount,
        status="pending"
    )


    db.add(new_order)
    db.flush()


    for product, quantity in order_products:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=quantity,
            price=product.price
        )


        product.stock -= quantity
        db.add(order_item)
    db.commit()


    return {
        "message": "Order created successfully",
        "order_id": new_order.id
    }


@router.get(
    "/seller",
    response_model=list[SellerOrderResponse]
)
def get_seller_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "seller":
        raise HTTPException(
            status_code=403,
            detail="Seller access required"
        )


    orders = (
        db.query(Order,OrderItem,Product,User)
        .join(
            OrderItem,
            Order.id == OrderItem.order_id
        )
        .join(
            Product,
            OrderItem.product_id == Product.id
        )
        .join(
            User,
            Order.customer_id == User.id
        )
        .filter(
            Product.seller_id == current_user.id
        )
        .order_by(
            Order.id.desc()
        )
        .all()
    )


    return [
        {
            "order_id": order.id,
            "customer_name": customer.full_name,
            "product_name": product.name,
            "product_image": product.image,
            "quantity": order_item.quantity,
            "price": order_item.price,
            "status": order.status,
        }

        for (
            order,
            order_item,
            product,
            customer
        ) in orders
    ]



@router.get(
    "/customer",
    response_model=list[CustomerOrderResponse]
)
def get_customer_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "customer":
        raise HTTPException(
            status_code=403,
            detail="Customer access required"
        )

    orders = (
        db.query(Order, OrderItem, Product)
        .join(
            OrderItem,
            Order.id == OrderItem.order_id
        )
        .join(
            Product,
            OrderItem.product_id == Product.id
        )
        .filter(
            Order.customer_id == current_user.id
        )
        .order_by(
            Order.id.desc()
        )
        .all()
    )

    return [
        {
            "order_id": order.id,
            "product_name": product.name,
            "product_image": product.image,
            "quantity": order_item.quantity,
            "price": order_item.price,
            "status": order.status,
        }

        for (
            order,
            order_item,
            product
        ) in orders
    ]