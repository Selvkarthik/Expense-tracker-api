from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict

class UserCreate(BaseModel):
    username : str = Field(min_length=1, max_length=50) 
    email : str = Field(min_length=1, max_length=120)
    password : str

class UserUpdate(BaseModel):
    username : str = Field(min_length=1, max_length=50)
    email : str = Field(min_length=1, max_length=120)

class TokenResponse(BaseModel):
    access_token : str
    token_type : str

class UserResponse(BaseModel):
    id : int
    username : str
    email : str
    created_at : datetime
    model_config = ConfigDict(from_attributes=True)

class ExpenseCreate(BaseModel):
    title : str = Field(min_length=1, max_length=50)
    amount : Decimal = Field(gt=0)
    description : str = Field(min_length=1, max_length=255)
    expense_date : date
    category_id : int = Field(gt=0)

class ExpenseResponse(BaseModel):
    id : int
    title : str
    amount : Decimal
    description : str
    expense_date : date
    category_id : int
    created_at : datetime

class CategoryCreate(BaseModel):
    name : str = Field(min_length=1, max_length=50)

class CategoryResponse(BaseModel):
    id : int
    name : str
    created_at : datetime

class BudgetCreate(BaseModel):
    month : int = Field(ge=1, le=12)
    year : int = Field(ge=2000)
    limit_amount : Decimal = Field(gt=0)

class BudgetResponse(BaseModel):
    id : int
    month : int
    year : int
    limit_amount : Decimal
    created_at : datetime