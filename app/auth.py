from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from dotenv import load_dotenv
import os

from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends

from .dependencies import db_dependency 
from . import models

load_dotenv()

SECRET_KEY = os.getenv('JWT_SECRET_KEY')
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

def create_access_token(data : dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({'exp' : expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)

    return encoded_jwt

def verify_token(token : str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get('sub')
        if user_id is None:
            raise HTTPException(status_code=401, detail='Could not validate credentials')
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail='Could not validate credentials')

def get_current_user(db : db_dependency, token : str = Depends(oauth2_scheme)):
    user_id = verify_token(token)
    user_data = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_data:
        raise HTTPException(status_code=401, detail='Could not validate credentials')
    return user_data