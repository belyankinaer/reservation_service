import uvicorn
from fastapi import FastAPI
from app.db_manager import create_database, create_tables, add_product

from app.routers import router

app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    create_database()
    create_tables()
    add_product("P001", "Продукт 1", 100)
    add_product("P002", "Продукт 2", 150)
    uvicorn.run("main:app", host="127.0.0.1", port=8000)