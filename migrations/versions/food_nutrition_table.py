"""Create food nutrition table

Revision ID: food_nutrition_table
Revises: google_health_models
Create Date: 2025-07-14

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'food_nutrition_table'
down_revision = 'google_health_models'
branch_labels = None
depends_on = None


def upgrade():
    # Create MealType enum
    meal_type_enum = postgresql.ENUM('breakfast', 'lunch', 'dinner', 'snack', 'brunch', 'supper', 'other', 
                                    name='mealtype')
    meal_type_enum.create(op.get_bind())
    
    # Create food_nutrition table
    op.create_table(
        'food_nutrition',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('food_name', sa.String(), nullable=False),
        sa.Column('serving_size', sa.String(), nullable=False),
        sa.Column('meal_type', sa.Enum('breakfast', 'lunch', 'dinner', 'snack', 'brunch', 'supper', 'other',
                                      name='mealtype'), nullable=False),
        sa.Column('nutrition', sa.JSON(), nullable=False),
        sa.Column('consumed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'food_name', 'serving_size', 'meal_type', 'consumed_at', 
                           name='uq_food_nutrition_entry')
    )
    op.create_index(op.f('ix_food_nutrition_id'), 'food_nutrition', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_food_nutrition_id'), table_name='food_nutrition')
    op.drop_table('food_nutrition')
    
    # Drop MealType enum
    postgresql.ENUM(name='mealtype').drop(op.get_bind())