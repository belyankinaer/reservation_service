

DB_HOST = "localhost"
DB_PORT = 5433
DB_USER = "postgres"
DB_PASS = "admin"
DB_NAME = "postgres"

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

#DATABASE_URL = "postgresql://postgres:admin@localhost:5433/postgres" # правильные настройки