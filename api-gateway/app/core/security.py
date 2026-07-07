from jose import jwt,JWTError
from app.core.config import settings

def verify_token(token:str):
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[
                settings.jwt_algorithm
            ]
        )
        return payload
    except JWTError:
        return None