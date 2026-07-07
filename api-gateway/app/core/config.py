

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    auth_service_url:str
    product_service_url:str
    order_service_url:str
    jwt_secret_key:str
    jwt_algorithm:str
    class Config:
        env_file=".env"
        case_sensitive=False

settings = Settings()