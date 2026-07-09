from app.schemas.order import Item
from enum import Enum


# class OrderStatus(Enum):
#     PENDING="PENDING"
#     CONFIRMED="CONFIRMED"
#     SHIPPED = "SHIPPED"
#     DELIVERED = "DELIVERED"
#     CANCELLED = "CANCELLED"
#     FAILED = "FAILED"

def cal_total_amount(items:Item):
    total = sum([item.quantity * item.price_at_purchase for item in items])
    return total