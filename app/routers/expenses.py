from fastapi import APIRouter, HTTPException, Depends, status, Query
from .. import models, schemas
from ..auth import get_current_user
from ..dependencies import db_dependency

router = APIRouter(prefix='/expenses', tags=['Expense'])

@router.post('/', response_model=schemas.ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(db : db_dependency, expense : schemas.ExpenseCreate, current_user = Depends(get_current_user)):
    category_data = db.query(models.Category).filter(models.Category.id == expense.category_id).first()
    if not category_data:
        raise HTTPException(status_code=404, detail='Category does not exist.')
    expense_data = models.Expense(
        title = expense.title,
        amount = expense.amount,
        description = expense.description,
        expense_date = expense.expense_date,
        category_id = expense.category_id,
        user_id = current_user.id
    )
    db.add(expense_data)
    db.commit()
    db.refresh(expense_data)
    return expense_data

@router.get('/', response_model=list[schemas.ExpenseResponse])
def get_expenses(db : db_dependency, skip : int = Query(0, ge=0), limit : int = Query(10, ge=1, le=100), current_user = Depends(get_current_user)):
    expense_data = db.query(models.Expense).filter(models.Expense.user_id == current_user.id).offset(skip).limit(limit).all()
    return expense_data

@router.get('/{expense_id}', response_model=schemas.ExpenseResponse)
def get_expense_id(db : db_dependency, expense_id : int, current_user = Depends(get_current_user)):
    expense_data = db.query(models.Expense).filter(models.Expense.id == expense_id, models.Expense.user_id == current_user.id).first()
    if not expense_data:
        raise HTTPException(status_code=404, detail='Expense does not exist.')
    return expense_data

@router.put('/{expense_id}', response_model=schemas.ExpenseResponse)
def update_expense(db : db_dependency, expense_id : int, expense : schemas.ExpenseCreate, current_user = Depends(get_current_user)):
    expense_data = db.query(models.Expense).filter(models.Expense.id == expense_id, models.Expense.user_id == current_user.id).first()
    if not expense_data:
        raise HTTPException(status_code=404, detail='Expense Does not exist.')
    expense_data.title = expense.title
    expense_data.amount = expense.amount
    expense_data.description = expense.description
    expense_data.expense_date = expense.expense_date
    expense_data.category_id = expense.category_id
    db.commit()
    db.refresh(expense_data)
    return expense_data

@router.delete('/{expense_id}')
def delete_expense(db : db_dependency, expense_id : int, current_user = Depends(get_current_user)):
    expense_data = db.query(models.Expense).filter(models.Expense.id == expense_id, models.Expense.user_id == current_user.id).first()
    if not expense_data:
        raise HTTPException(status_code=404, detail='Expense data not Found.')
    db.delete(expense_data)
    db.commit()
    return {'Message' : 'Expense data Deleted Successfully.'}