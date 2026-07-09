from app.db.database import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,DateTime
import uuid
from sqlalchemy.orm import relationship
from datetime import datetime,timezone
class Product(Base):
    __tablename__ = "products"
    id = Column(
                UUID(as_uuid=True), 
                primary_key=True, 
                default=uuid.uuid4,
                index=True
                )
    name = Column(String,unique=True,index=True)
    description = Column(String)
    price = Column(Integer)
    category_id = Column(Integer,ForeignKey("categories.id",ondelete="CASCADE"),nullable=False)
    stock_quantity = Column(Integer)
    image_url = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), 
                        default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
    
    category = relationship("Category")