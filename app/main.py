from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import or_
from .dependencies import db_dependency
from .database import engine
from . import models
from . import schemas
from .security import hash_password, verify_password
from .auth import create_access_token, get_current_user

app = FastAPI(title='Expense Tracker API')

@app.get('/')
def root():
    return {"Message" : "App running successfully"}

@app.post('/auth/login', response_model=schemas.TokenResponse)
def authentication(db : db_dependency, form_data : OAuth2PasswordRequestForm = Depends()):
    user_data = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user_data:
        raise HTTPException(status_code=401, detail='Invalid Username or Password')
    if not verify_password(form_data.password, user_data.password_hash):
        raise HTTPException(status_code=401, detail='Invalid Username or Password')
    token = create_access_token({"sub" : str(user_data.id)})
    return {"access_token" : token,
            "token_type" : "bearer"}

@app.get('/auth/me')
def get_me(current_user = Depends(get_current_user)):
    return current_user

@app.post('/users/', response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user : schemas.UserCreate, db : db_dependency):
    existing_user = db.query(models.User).filter(or_(models.User.username == user.username, models.User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=409, detail='Username or Email already exists')
    hashed_password = hash_password(user.password)
    user_data = models.User(
        username = user.username,
        email = user.email,
        password_hash = hashed_password
    )
    db.add(user_data)
    db.commit()
    db.refresh(user_data)
    return user_data

@app.get('/users/', response_model=list[schemas.UserResponse])
def get_users(db : db_dependency, skip : int = Query(0, ge=0), limit : int = Query(10, ge=1, le=100)):
    user_data = db.query(models.User).offset(skip).limit(limit).all()
    return user_data

@app.get('/users/{user_id}', response_model=schemas.UserResponse)
def get_user_id(db: db_dependency, user_id : int):
    user_data = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_data:
        raise HTTPException(status_code=404, detail='User Not Found')
    return user_data

@app.put('/users/{user_id}', response_model=schemas.UserResponse)
def update_user(db : db_dependency, user_id : int, user_change : schemas.UserUpdate):
    user_data = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_data:
        raise HTTPException(status_code=404, detail='User Not Found')
    user_data.username = user_change.username
    user_data.email = user_change.email
    db.commit()
    db.refresh(user_data)
    return user_data

@app.delete('/users/{user_id}')
def delete_user(db : db_dependency, user_id : int):
    user_data = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_data:
        raise HTTPException(status_code=404, detail='User Not Found')
    db.delete(user_data)
    db.commit()
    return {"Message" : "User data deleted successfully"}