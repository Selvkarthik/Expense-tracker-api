from ..import models, schemas
from ..dependencies import db_dependency
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from ..security import verify_password
from ..auth import create_access_token, get_current_user

router = APIRouter(prefix='/auth', tags=['Auth'])

@router.post('/login', response_model=schemas.TokenResponse)
def authentication(db : db_dependency, form_data : OAuth2PasswordRequestForm = Depends()):
    user_data = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user_data:
        raise HTTPException(status_code=401, detail='Invalid Username or Password.')
    if not verify_password(form_data.password, user_data.password_hash):
        raise HTTPException(status_code=401, detail='Invalid Username or Password.')
    token = create_access_token({"sub" : str(user_data.id)})
    return {"access_token" : token,
            "token_type" : "bearer"}

@router.get('/me', response_model=schemas.UserResponse)
def get_me(current_user = Depends(get_current_user)):
    return current_user