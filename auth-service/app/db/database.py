# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# import os
# from app.core.config import settings

# win_host_ip = os.popen("ip route show | grep default | awk '{print $3}'").read().strip()

# SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg://{settings.database_username}:{settings.database_password}@{win_host_ip}/{settings.database_name}"

# engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

# Base = declarative_base()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import os
from app.core.config import settings

win_host_ip = os.popen("ip route show | grep default | awk '{print $3}'").read().strip()

SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{settings.database_username}:{settings.database_password}@{win_host_ip}/{settings.database_name}"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL,echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind = engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            pass