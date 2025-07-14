"""Create meal entries table

Revision ID: meal_entries_table
Revises: food_nutrition_table
Create Date: 2025-07-14

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'meal_entries_table'
down_revision = 'food_nutrition_table'
branch_labels = None
depends_on = None


def upgrade():
    # Create MealType enum
    meal_type_enum = postgresql.ENUM('breakfast', 'lunch', 'dinner', 'snack', 'brunch', 'supper', 'other', 
                                    name='mealtype')
    
    # Check if enum already exists (from previous migration)
    conn = op.get_bind()
    if not conn.dialect.has_type(conn, 'mealtype'):
        meal_type_enum.create(op.get_bind())
    
    # Create meal_entries table
    op.create_table(
        'meal_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('meal_type', sa.Enum('breakfast', 'lunch', 'dinner', 'snack', 'brunch', 'supper', 'other', 
                                      name='mealtype'), nullable=False),
        sa.Column('foods', sa.JSON(), nullable=False),
        sa.Column('consumed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'meal_type', 'consumed_at', name='uq_meal_entry')
    )
    op.create_index(op.f('ix_meal_entries_id'), 'meal_entries', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_meal_entries_id'), table_name='meal_entries')
    op.drop_table('meal_entries')
    
    # Don't drop the MealType enum as it might be used by other tables