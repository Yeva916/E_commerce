from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname:str
    database_port:str
    database_password:str
    database_name:str
    database_username:str
    jwt_secret_key:str
    jwt_algorithm:str
    access_token_expire_minutes:int
    google_client_id:str
    google_client_secret:str
    google_redirect_uri:str
    resend_api_key:str
    base_url:str
    refresh_token_expire_days:int
    class Config:
        env_file = ".env"
        case_sensitive = False
settings = Settings()