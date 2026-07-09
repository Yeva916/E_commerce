from sqlalchemy.dialects.postgresql import UUID

from app.db.database import Base
from enum import Enum
import uuid
from sqlalchemy import TIMESTAMP, Boolean, Column, String, text,Enum as SQLEnum
# from sqlalchemy.types import Enum as SQLEnum

class AuthProvider(Enum):
    EMAIL = "email"
    GOOGLE = "google"
    # FACEBOOK = "facebook"
class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    auth_provider = Column(SQLEnum(AuthProvider), default=AuthProvider.EMAIL) # email, google, facebook
    provider_user_id = Column(String, nullable=True) # for social login
    role = Column(String, default="user")
    is_verified = Column(Boolean, default=False) 
    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))

