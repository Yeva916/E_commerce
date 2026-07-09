from app.db.database import Base
from sqlalchemy import Boolean, Column, Integer, String

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True,index=True)
    name = Column(String,unique=True,index=True)
    description = Column(String)
    is_archived = Column(Boolean,default=False)