

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    rabbitmq_url:str
    auth_service_url:str
    product_service_url:str
    order_service_url:str

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()