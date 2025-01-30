"""Create role enum and update users table

Revision ID: cfff69912726
Revises: c698154d4a21
Create Date: 2025-01-30 02:31:36.776720

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'cfff69912726'
down_revision: Union[str, None] = 'c698154d4a21'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Создаем ENUM тип вручную
    role_enum = postgresql.ENUM('USER', 'VOLUNTEER', 'ADMIN', name='role', create_type=True)
    role_enum.create(op.get_bind(), checkfirst=True)

    # Изменяем колонку с конвертацией данных
    op.alter_column('users', 'role',
                   type_=role_enum,
                   postgresql_using='role::text::role',  # Конвертация существующих значений
                   nullable=True)

def downgrade() -> None:
    # Возвращаем обратно VARCHAR тип
    op.alter_column('users', 'role',
                   type_=sa.VARCHAR(),
                   postgresql_using='role::text',  # Конвертация обратно в текст
                   nullable=True)
    
    # Удаляем ENUM тип
    role_enum = postgresql.ENUM('USER', 'VOLUNTEER', 'ADMIN', name='role')
    role_enum.drop(op.get_bind(), checkfirst=True)