from fastapi import FastAPI
from app.api import calculate

print("🔧 MAIN APP LOADED 🔧")

app = FastAPI()


app.include_router(calculate.router)
