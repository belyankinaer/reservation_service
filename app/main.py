import uvicorn
from fastapi import FastAPI

from app.constants import SERVICE_HOST, SERVICE_PORT
from app.routers import router

app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host=SERVICE_HOST, port=SERVICE_PORT)
