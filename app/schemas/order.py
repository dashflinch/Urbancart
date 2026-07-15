from pydantic import BaseModel


class OrderItemCreate(BaseModel):

    product_id: int
    quantity: int


class OrderCreate(BaseModel):

    items: list[OrderItemCreate]


class OrderItemResponse(BaseModel):

    id: int
    product_id: int
    quantity: int
    price: float

    class Config:
        from_attributes = True


class SellerOrderResponse(BaseModel):

    order_id: int
    customer_name: str
    product_name: str
    product_image: str
    quantity: int
    price: float
    status: str


class CustomerOrderResponse(BaseModel):
    order_id: int
    product_name: str
    product_image: str
    quantity: int
    price: float
    status: str

    class Config:
        from_attributes = True