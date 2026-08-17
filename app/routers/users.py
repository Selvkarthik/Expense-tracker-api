from fastapi import APIRouter, status, HTTPException, Query
from .. import models, schemas
from ..security import hash_password
from ..dependencies import db_dependency
from sqlalchemy import or_

router = APIRouter(prefix='/users', tags=['Users'])

@router.post('/', response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user : schemas.UserCreate, db : db_dependency):
    existing_user = db.query(models.User).filter(or_(models.User.username == user.username, models.User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=409, detail='Username or Email already exists.')
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

@router.get('/', response_model=list[schemas.UserResponse])
def get_users(db : db_dependency, skip : int = Query(0, ge=0), limit : int = Query(10, ge=1, le=100)):
    user_data = db.query(models.User).offset(skip).limit(limit).all()
    return user_data

@router.get('/{user_id}', response_model=schemas.UserResponse)
def get_user_id(db: db_dependency, user_id : int):
    user_data = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_data:
        raise HTTPException(status_code=404, detail='User Not Found.')
    return user_data

@router.put('/{user_id}', response_model=schemas.UserResponse)
def update_user(db : db_dependency, user_id : int, user_change : schemas.UserUpdate):
    user_data = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_data:
        raise HTTPException(status_code=404, detail='User Not Found.')
    user_data.username = user_change.username
    user_data.email = user_change.email
    db.commit()
    db.refresh(user_data)
    return user_data

@router.delete('/{user_id}')
def delete_user(db : db_dependency, user_id : int):
    user_data = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_data:
        raise HTTPException(status_code=404, detail='User Not Found.')
    db.delete(user_data)
    db.commit()
    return {"Message" : "User data deleted successfully."}