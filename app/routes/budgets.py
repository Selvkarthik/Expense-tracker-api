from fastapi import APIRouter, Depends, HTTPException, status, Query
from .. import models, schemas
from ..dependencies import db_dependency
from ..auth import get_current_user

router = APIRouter(prefix='/budgets', tags=['Budgets'])

@router.post('/', response_model=schemas.BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(db : db_dependency, budget : schemas.BudgetCreate, current_user = Depends(get_current_user)):
    existing_budget = db.query(models.Budget).filter(
        models.Budget.user_id == current_user.id,
        models.Budget.month == budget.month,
        models.Budget.year == budget.year
    ).first()
    if existing_budget:
        raise HTTPException(status_code=409, detail='Budget already exists.')
    budget_data = models.Budget(
        month = budget.month,
        year = budget.year,
        limit_amount = budget.limit_amount,
        user_id = current_user.id
    )
    db.add(budget_data)
    db.commit()
    db.refresh(budget_data)
    return budget_data

@router.get('/', response_model=list[schemas.BudgetResponse])
def get_budgets(db : db_dependency, skip : int = Query(0, ge=0), limit : int = Query(10, ge=1, le=100), current_user = Depends(get_current_user)):
    budget_data = db.query(models.Budget).filter(models.Budget.user_id == current_user.id).offset(skip).limit(limit).all()
    return budget_data

@router.get('/{budget_id}', response_model=schemas.BudgetResponse)
def get_budget_id(db : db_dependency, budget_id : int, current_user = Depends(get_current_user)):
    budget_data = db.query(models.Budget).filter(models.Budget.id == budget_id, models.Budget.user_id == current_user.id).first()
    if not budget_data:
        raise HTTPException(status_code=404, detail='Budget data not Found.')
    return budget_data

@router.put('/{budget_id}', response_model=schemas.BudgetResponse)
def update_budget(db : db_dependency, budget_id : int, budget : schemas.BudgetCreate, current_user = Depends(get_current_user)):
    budget_data = db.query(models.Budget).filter(models.Budget.id == budget_id, models.Budget.user_id == current_user.id).first()
    if not budget_data:
        raise HTTPException(status_code=404, detail='Budget data not Found.')
    existing_data = db.query(models.Budget).filter(
        models.Budget.user_id == current_user.id,
        models.Budget.month == budget.month,
        models.Budget.year == budget.year,
        models.Budget.id != budget_id
    ).first()
    if existing_data:
        raise HTTPException(status_code=409, detail='Cannot update Budget already exists.')
    budget_data.month = budget.month
    budget_data.year = budget.year
    budget_data.limit_amount = budget.limit_amount
    db.commit()
    db.refresh(budget_data)
    return budget_data

@router.delete('/{budget_id}')
def delete_budget(db : db_dependency, budget_id : int, current_user = Depends(get_current_user)):
    budget_data = db.query(models.Budget).filter(models.Budget.id == budget_id, models.Budget.user_id == current_user.id).first()
    if not budget_data:
        raise HTTPException(status_code=404, detail='Budget data not Found.')
    db.delete(budget_data)
    db.commit()
    return {'Message' : 'Budget data Deleted Successfully.'}