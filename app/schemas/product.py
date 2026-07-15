from pydantic import BaseModel


class ProductCreate(BaseModel):

    name: str
    description: str | None = None
    price: float
    stock: int
    image: str | None = None


class ProductResponse(BaseModel):

    id: int
    name: str
    description: str | None
    price: float
    stock: int
    image: str | None
    seller_id: int


    class Config:
        from_attributes = True

class SellerDashboardResponse(BaseModel):
    seller_name: str
    total_products: int
    total_orders: int
    total_revenue: float
    total_customers: int
    recent_products: list[ProductResponse]