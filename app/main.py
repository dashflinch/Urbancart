from fastapi import FastAPI
from app.models.product import Product
from app.database import Base, engine
from app.models.user import User
from app.routes.auth import router as auth_router
from app.routes.seller import router as seller_router
from app.routes.product import router as product_router
from app.models.order import Order
from app.models.order_item import OrderItem
from app.routes.order import router as order_router
from app.routes import message
from app.models.message import Message

app = FastAPI(
    title="UrbanCart API"
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(seller_router)
app.include_router(product_router)
app.include_router(order_router)
app.include_router(message.router)



@app.get("/")
def root():
    return {
        "message": "UrbanCart Backend Running Successfully"
    }