from fastapi import FastAPI
from .routers import users, auth, categories

app = FastAPI(title='Expense Tracker API')
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(categories.router)

@app.get('/')
def root():
    return {"Message" : "App running successfully"}