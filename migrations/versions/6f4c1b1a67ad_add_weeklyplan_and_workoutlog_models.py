"""Add WeeklyPlan and WorkoutLog models

Revision ID: 6f4c1b1a67ad
Revises: 7a5ec745e1fd
Create Date: 2025-05-07 00:15:35.514483

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f4c1b1a67ad'
down_revision = '7a5ec745e1fd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('weekly_plans',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('plan_name', sa.String(length=100), nullable=False),
    sa.Column('calorie_goal', sa.Integer(), nullable=False),
    sa.Column('time_goal_minutes', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('workout_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('plan_name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('duration_minutes', sa.Integer(), nullable=False),
    sa.Column('workout_type', sa.String(length=50), nullable=False),
    sa.Column('calories', sa.Integer(), nullable=True),
    sa.Column('intensity', sa.String(length=50), nullable=True),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('workout_days', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('workout_logs')
    op.drop_table('weekly_plans')
    # ### end Alembic commands ###
