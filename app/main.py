from fastapi import FastAPI
from app.api import calculate

app = FastAPI()

# 🚨 THIS IS CRUCIAL
app.include_router(calculate.router)
