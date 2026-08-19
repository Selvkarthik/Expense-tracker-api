from fastapi import APIRouter, HTTPException, status, Query
from .. import schemas, models
from ..dependencies import db_dependency

router = APIRouter(prefix='/categories', tags=['Categories'])

@router.post('/', response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(db : db_dependency, category : schemas.CategoryCreate):
    existing_category = db.query(models.Category).filter(models.Category.name == category.name).first()
    if existing_category:
        raise HTTPException(status_code=409, detail='Category already exists.')
    category_data = models.Category(
        name = category.name
    )
    db.add(category_data)
    db.commit()
    db.refresh(category_data)
    return category_data

@router.get('/', response_model=list[schemas.CategoryResponse])
def get_categories(db : db_dependency, skip : int = Query(0, ge=0), limit : int = Query(10, ge=1, le=100)):
    category_data = db.query(models.Category).offset(skip).limit(limit).all()
    return category_data

@router.get('/{category_id}', response_model=schemas.CategoryResponse)
def get_category_id(db : db_dependency, category_id : int):
    category_data = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category_data:
        raise HTTPException(status_code=404, detail='Category Not Found.')
    return category_data

@router.put('/{category_id}', response_model=schemas.CategoryResponse)
def update_category(db : db_dependency, category_id : int, category_change : schemas.CategoryCreate):
    existing_category = db.query(models.Category).filter(models.Category.name == category_change.name, models.Category.id != category_id).first()
    if existing_category:
        raise HTTPException(status_code=409, detail="Category already exists.")
    category_data = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category_data:
        raise HTTPException(status_code=404, detail='Category does not Exist.')
    category_data.name = category_change.name
    db.commit()
    db.refresh(category_data)
    return category_data

@router.delete('/{category_id}')
def delete_category(db : db_dependency, category_id : int):
    category_data = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category_data:
        raise HTTPException(status_code=404, detail='Category Not Found.')
    caategor_expense_data = db.query(models.Expense).filter(models.Expense.category_id == category_id).first()
    if caategor_expense_data:
        raise HTTPException(status_code=409, detail='Category cannot be deleted because it is being used by an expense.')
    db.delete(category_data)
    db.commit()
    return {'Message' : 'Category Deleted Successfully.'}