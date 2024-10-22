
SERVICE_HOST = '0.0.0.0'
SERVICE_PORT = 8000


# DB_HOST = "localhost"
DB_HOST = "0.0.0.0"
# DB_PORT = 5433
DB_PORT = 5432
DB_NAME = "reservation_service"
DB_PASS = "admin"
DB_USER = "postgres"


DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
URL_POSTGRES = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}"
#DATABASE_URL = "postgresql://postgres:admin@localhost:5433/postgres" # правильные настройки