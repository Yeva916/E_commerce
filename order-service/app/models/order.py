from enum import Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy import Column,DateTime,Enum as SQLEnum, ForeignKey, Integer, Numeric
from datetime import datetime,timezone
from app.db.database import Base
from sqlalchemy.orm import relationship

class OrderStatus(Enum):
    PENDING="PENDING"
    CONFIRMED="CONFIRMED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"

class Orders(Base):
    __tablename__ = "orders"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    user_id = Column(UUID(as_uuid=True),nullable=False)
    status = Column(SQLEnum(OrderStatus),default=OrderStatus.PENDING)
    total_amount = Column(Numeric(precision=10,scale=2),nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), 
                        default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
    
    items = relationship("OrderItem",backref='order',cascade="all, delete-orphan")



class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    order_id = Column(UUID(as_uuid=True),ForeignKey("orders.id",ondelete="CASCADE"),nullable=False)
    product_id = Column(UUID(as_uuid=True),nullable=False)
    quantity = Column(Integer,nullable=False,default=1)
    price_at_purchase = Column(Numeric(precision=10,scale=2),nullable=False)
