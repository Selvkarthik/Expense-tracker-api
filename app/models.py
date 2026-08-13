from sqlalchemy import String, Numeric, ForeignKey, DateTime, func, UniqueConstraint, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, date
from decimal import Decimal
from .database import Base

class User(Base):
    __tablename__  = 'users'

    id : Mapped[int] = mapped_column(primary_key=True)
    username : Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email : Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash : Mapped[str] = mapped_column(String(255), nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    expenses : Mapped[list["Expense"]] = relationship(back_populates='user')
    budgets : Mapped[list["Budget"]] = relationship(back_populates='user')

class Expense(Base):
    __tablename__ = 'expenses'

    id : Mapped[int] = mapped_column(primary_key=True)
    title : Mapped[str] = mapped_column(String(50), nullable=False)
    amount : Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    description : Mapped[str] = mapped_column(String(255), nullable=False)
    expense_date : Mapped[date] = mapped_column(Date, nullable=False)
    user_id : Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    category_id : Mapped[int] = mapped_column(ForeignKey('categories.id'), nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    user : Mapped['User'] = relationship(back_populates='expenses')
    category : Mapped['Category'] = relationship(back_populates='expenses')

class Category(Base):
    __tablename__ = 'categories'

    id : Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    expenses : Mapped[list['Expense']] = relationship(back_populates='category')

class Budget(Base):
    __tablename__ = 'budgets'
    id : Mapped[int] = mapped_column(primary_key=True)
    month : Mapped[int] = mapped_column(nullable=False)
    year : Mapped[int] = mapped_column(nullable=False)
    limit_amount : Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    user_id : Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    user : Mapped['User'] = relationship(back_populates='budgets')

    __table_args__ = (UniqueConstraint('user_id', 'month', 'year', name='uq_user_budget_month'), )