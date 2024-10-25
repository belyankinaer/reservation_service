"""Initial migration

Revision ID: f802b66cbd2d
Revises: 
Create Date: 2024-10-25 09:55:51.268920

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError

revision: str = 'f802b66cbd2d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def create_database_if_not_exists(url: str) -> None:
    engine = create_engine(url.rsplit('/', 1)[0])
    database_name = url.split('/')[-1]

    try:
        with engine.connect() as connection:
            connection.execute(f"CREATE DATABASE {database_name}")
            print(f"Database '{database_name}' created.")
    except ProgrammingError:
        print(f"Database '{database_name}' already exists.")

def upgrade() -> None:
    config = op.get_context().config
    database_url = config.get_main_option("sqlalchemy.url")

    create_database_if_not_exists(database_url)

    op.create_table('products',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('product_id', sa.String(length=50), nullable=False, unique=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.current_timestamp(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp(), nullable=True)
    )

    op.create_table('reservations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('reservation_id', sa.String(length=50), nullable=False, unique=True),
        sa.Column('product_id', sa.String(length=50), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.TIMESTAMP(timezone=True), server_default=sa.func.current_timestamp(), nullable=True),
        sa.Column('status', sa.String(length=20), default='pending'),
        sa.ForeignKeyConstraint(['product_id'], ['products.product_id'])
    )

def downgrade() -> None:
    op.drop_table('reservations')
    op.drop_table('products')