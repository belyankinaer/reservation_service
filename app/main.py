import asyncio
import uvicorn
from fastapi import FastAPI

from app.constants import SERVICE_HOST, SERVICE_PORT
from app.db_manager import DatabaseManager
from app.routers import router

app = FastAPI()
app.include_router(router)

db_manager = DatabaseManager()

async def main():
    asyncio.run(db_manager.create_database())
    await db_manager.create_tables()
    await db_manager.add_product("P001", "Продукт 1", 100)
    await db_manager.add_product("P002", "Продукт 2", 150)

if __name__ == "__main__":
    asyncio.run(main())  # Run the main async function
    #uvicorn.run(app, host="127.0.0.1", port=8000)  # Start the FastAPI app
    uvicorn.run(app, host=SERVICE_HOST, port=SERVICE_PORT)  # Start the FastAPI app