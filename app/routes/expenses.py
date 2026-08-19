from fastapi import APIRouter, HTTPException, Depends, status, Query
from .. import models, schemas
from ..auth import get_current_user
from ..dependencies import db_dependency
from datetime import date
import calendar
from sqlalchemy import func

router = APIRouter(prefix='/expenses', tags=['Expense'])

@router.post('/', response_model=schemas.ExpenseCreateResponse, status_code=status.HTTP_201_CREATED)
def create_expense(db : db_dependency, expense : schemas.ExpenseCreate, current_user = Depends(get_current_user)):
    category_data = db.query(models.Category).filter(models.Category.id == expense.category_id).first()
    if not category_data:
        raise HTTPException(status_code=404, detail='Category does not exist.')
    
    budget_data = db.query(models.Budget).filter(
        models.Budget.user_id == current_user.id,
        models.Budget.month == expense.expense_date.month,
        models.Budget.year == expense.expense_date.year
    ).first()

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

    budget_warning = None

    if budget_data:
        start_date = date(budget_data.year, budget_data.month, 1)
        last_day = calendar.monthrange(budget_data.year, budget_data.month)[1]
        end_date = date(budget_data.year, budget_data.month, last_day)

        total_spent = db.query(func.sum(models.Expense.amount)).filter(
            models.Expense.user_id == current_user.id,
            models.Expense.expense_date >= start_date,
            models.Expense.expense_date <= end_date
        ).scalar()

        total_spent = total_spent or 0
        budget_exceeded = total_spent > budget_data.limit_amount
        if budget_exceeded:
            exceeded_by = total_spent - budget_data.limit_amount
        else:
            exceeded_by = 0

        budget_warning = schemas.BudgetWarning(exceeded=budget_exceeded, exceeded_by=exceeded_by)

    return {'expense' : expense_data, 'budget_warning' : budget_warning}

@router.get('/', response_model=list[schemas.ExpenseResponse])
def get_expenses(
    db : db_dependency, 
    skip : int = Query(0, ge=0), 
    limit : int = Query(10, ge=1, le=100),
    category_id : int | None = Query(None, gt=0), 
    start_date : date | None = Query(None),
    end_date : date | None = Query(None),
    sort_by : schemas.ExpenseSortBy = Query(schemas.ExpenseSortBy.expense_date),
    sort_order : schemas.SortOrder = Query(schemas.SortOrder.desc),
    current_user = Depends(get_current_user)
    ):
    sort_columns = {
        schemas.ExpenseSortBy.expense_date : models.Expense.expense_date,
        schemas.ExpenseSortBy.amount : models.Expense.amount,
        schemas.ExpenseSortBy.created_at : models.Expense.created_at,
        schemas.ExpenseSortBy.title : models.Expense.title
    }
    sort_column = sort_columns[sort_by]

    query = db.query(models.Expense).filter(models.Expense.user_id == current_user.id)

    if category_id is not None:
        query = query.filter(models.Expense.category_id == category_id)
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail='Start date cannot be after end date')
    if start_date:
        query = query.filter(models.Expense.expense_date >= start_date)
    if end_date:
        query = query.filter(models.Expense.expense_date <= end_date)
    if sort_order == schemas.SortOrder.asc:
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
        
    expense_data = query.offset(skip).limit(limit).all()
    return expense_data

@router.get('/summary')
def get_expense_summary(
    db : db_dependency,
    month : int | None = Query(None, ge=1, le=12),
    year : int | None = Query(None, ge=2000),
    current_user = Depends(get_current_user)
    ):

    query = db.query(models.Expense).filter(models.Expense.user_id == current_user.id)

    if month is not None:
        if year is None:
            year = date.today().year
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date =  date(year, month, last_day)

        query = query.filter(models.Expense.expense_date >= start_date, models.Expense.expense_date <= end_date)

    elif year is not None:
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

        query = query.filter(models.Expense.expense_date >= start_date, models.Expense.expense_date <= end_date)

    total = query.with_entities(func.sum(models.Expense.amount)).scalar()
    count = query.with_entities(func.count(models.Expense.id)).scalar()
    average = query.with_entities(func.avg(models.Expense.amount)).scalar()

    return {
        'total_expense ' : total or 0,
        'expense_count' : count or 0,
        'average_expense' : average or 0
        }


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