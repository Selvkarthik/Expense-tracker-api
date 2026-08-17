from fastapi import FastAPI
from .routers import auth, users, categories, expenses

app = FastAPI(title='Expense Tracker API')

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(expenses.router)

@app.get('/')
def root():
    return {"Message" : "App running successfully"}