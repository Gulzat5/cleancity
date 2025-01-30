"""Fix Enum models

Revision ID: e5f9ab4c7b5b
Revises: cfff69912726
Create Date: 2025-01-30 03:06:15.383132

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e5f9ab4c7b5b'
down_revision: Union[str, None] = 'cfff69912726'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Создаем ENUM тип "status" вручную
    status_enum = postgresql.ENUM(
        'pending', 'approved', 'rejected', 'in_progress', 'resolved', 
        name='status',
        create_type=True
    )
    status_enum.create(op.get_bind(), checkfirst=True)

    # Затем изменяем колонку
    op.alter_column('complaints', 'status',
                   type_=status_enum,
                   postgresql_using='status::text::status',  # Конвертация
                   nullable=True)

def downgrade():
    # Возвращаем тип колонки обратно
    op.alter_column('complaints', 'status',
                   type_=sa.VARCHAR(),
                   postgresql_using='status::text',
                   nullable=True)
    
    # Удаляем ENUM тип
    status_enum = postgresql.ENUM(name='status')
    status_enum.drop(op.get_bind(), checkfirst=True)