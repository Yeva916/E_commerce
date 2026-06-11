from passlib.context import CryptContext
import resend.emails
from app.core.config import settings
from datetime import datetime,timedelta,timezone
from jose import JWTError, jwt
import resend

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)

def create_access_token(payload: dict):
    to_encode = payload.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp":int(expire.timestamp())})

    if "sub" in to_encode and not isinstance(to_encode["sub"], str):
        to_encode["sub"] = str(to_encode["sub"])
    
    encoded_jwt = jwt.encode(to_encode,settings.jwt_secret_key,algorithm=settings.jwt_algorithm)
    return encoded_jwt

def create_refresh_token(payload:dict):
    to_encode = payload.copy()

    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp":int(expire.timestamp())})

    if "sub" in to_encode and not isinstance(to_encode["sub"], str):
        to_encode["sub"] = str(to_encode["sub"])
    
    encoded_jwt = jwt.encode(to_encode,settings.jwt_secret_key,algorithm=settings.jwt_algorithm)
    return encoded_jwt

def decode_access_token(token: str):

    try:

        if not isinstance(token, str):
            token = str(token)

        token = token.strip().strip('"')

        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm], options={"verify_exp": False})

        return payload
    except JWTError as e:
        print(f"JWT decoding error: {e}")
        return None

def create_verification_token(email:str):
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": email,
        "exp": int(expire.timestamp())
    }

    return jwt.encode(payload,settings.jwt_secret_key,algorithm=settings.jwt_algorithm)

def create_password_reset_token(email:str):
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": email,
        "exp": int(expire.timestamp())
    }

    return jwt.encode(payload,settings.jwt_secret_key,algorithm=settings.jwt_algorithm)