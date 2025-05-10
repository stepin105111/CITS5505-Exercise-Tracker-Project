"""Add friendship table

Revision ID: 91394359c9d4
Revises: d859d14a9153
Create Date: 2025-05-10 17:32:27.829625

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '91394359c9d4'
down_revision = 'd859d14a9153'
branch_labels = None
depends_on = None


def upgrade():
    # Create friendships table
    op.create_table('friendships',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('friend_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['friend_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'friend_id')
    )


def downgrade():
    # Drop friendships table
    op.drop_table('friendships')
