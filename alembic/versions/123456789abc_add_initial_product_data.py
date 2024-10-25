"""Add initial product data

Revision ID: 123456789abc
Revises: f802b66cbd2d
Create Date: 2024-10-25 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

revision: str = '123456789abc'
down_revision: str = 'f802b66cbd2d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

products_table = table(
    'products',
    column('product_id', sa.String(length=50)),
    column('name', sa.String(length=100)),
    column('quantity', sa.Integer()),
)

def upgrade() -> None:
    op.bulk_insert(
        products_table,
        [
            {
                'product_id': 'P001',
                'name': 'Product 1',
                'quantity': 100,
            },
            {
                'product_id': 'P002',
                'name': 'Product 2',
                'quantity': 50,
            }
        ]
    )

def downgrade() -> None:
    op.execute("DELETE FROM products WHERE product_id IN ('P001', 'P002')")