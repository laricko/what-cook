"""constraint_for_step_order

Revision ID: 2a7f532916a1
Revises: e8e22cf19bbb
Create Date: 2023-01-04 02:47:05.405721

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2a7f532916a1"
down_revision = "e8e22cf19bbb"
branch_labels = None
depends_on = None


def upgrade():
    op.create_check_constraint("ck_step_order_positive", "step", "step.order > 0")


def downgrade():
    op.drop_constraint("ck_step_order_positive", "step", "check")
