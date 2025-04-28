"""Add superadmin and superadmin_readonly to user_role_enum

Revision ID: 1cec8cbbbc4b
Revises: f2140c3090fd
Create Date: 2025-04-28 14:28:20.556829

"""
from ast import Pass
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1cec8cbbbc4b'
down_revision = 'f2140c3090fd'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE user_role_enum ADD VALUE 'superadmin'")
    op.execute("ALTER TYPE user_role_enum ADD VALUE 'superadmin_readonly'")


def downgrade():
    Pass
