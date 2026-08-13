from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Annotated
from .database import engine, get_db
from . import models
from . import schemas
from .security import hash_password

app = FastAPI(title='Expense Tracker API')

db_dependency = Annotated[Session, Depends(get_db)]

@app.get('/')
def root():
    return {"Message" : "App running successfully"}

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