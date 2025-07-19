#!/bin/bash
set -e

# Function to run a SQL command as the postgres user
psql_command() {
  psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -c "$1"
}

echo "PostgreSQL initialization script running..."

# Create extensions if needed
psql_command "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"

echo "PostgreSQL initialization completed."