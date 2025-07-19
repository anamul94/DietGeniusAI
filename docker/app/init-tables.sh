#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."
# Wait for PostgreSQL to be ready
# Use default values if environment variables are not set
PGPASS=${POSTGRES_PASSWORD:-password}
PGUSER=${POSTGRES_USER:-postgres}
PGDB=${POSTGRES_DB:-dietgenius}

until PGPASSWORD=$PGPASS psql -h db -U $PGUSER -d $PGDB -c '\q'; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - initializing database tables"

# Run database migrations using alembic
alembic upgrade head

# Create tables using SQLAlchemy models
python -c "
from app.db.create_tables import create_all_tables
create_all_tables()
print('Database tables created successfully')
"

echo "Database initialization completed"