from app.schemas.order import Item

def cal_total_amount(items:Item):
    total = sum([item.quantity * item.price_at_purchase for item in items])
    return total