from fastapi import FastAPI
from .database import engine
from . import models

app = FastAPI(title='Expense Tracker API')

models.Base.metadata.create_all(bind=engine)

@app.get('/')
def root():
    return {"Message" : "App running successfully"}