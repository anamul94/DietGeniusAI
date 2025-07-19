# Docker Setup for DietGeniusAI

This document explains how to use the Docker Compose setup and Makefile commands for the DietGeniusAI project.

## Prerequisites

- Docker and Docker Compose installed on your system
- Git (optional, for version information)
- uv package manager (used instead of pip)

## Environment Setup

1. Copy the example environment file and configure it:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and set the required variables:
   ```
   POSTGRES_DB=dietgenius
   POSTGRES_USER=user
   POSTGRES_PASSWORD=your_secure_password
   SECRET_KEY=your_secret_key_here
   ```

## Docker Commands

### Starting the Application

To build and start all services:

```bash
make setup
```

This command will:
1. Build all Docker images
2. Start all containers
3. Initialize the database and create tables

### Managing Services

- **Start services**: `make up`
- **Stop services**: `make down`
- **View logs**: `make logs`
- **Access app shell**: `make shell`
- **Access database shell**: `make db-shell`

### Database Management

- **Initialize database**: `make db-init`
- **Reset database**: `make db-reset`
- **Run migrations**: `make migrate`
- **Create new migration**: `make migration msg="your message"`
- **Show migration history**: `make db-history`

### Development

- **Install dependencies locally**: `make install` (uses uv instead of pip)
- **Run development server**: `make dev`
- **Run tests**: `make test`
- **Format code**: `make format`
- **Lint code**: `make lint`

## Docker Compose Services

The setup includes the following services:

1. **app**: The FastAPI application
   - Port: 8000
   - Depends on: db

2. **db**: PostgreSQL database
   - Port: 5338 (mapped to 5432 inside container)
   - Data persistence: ./data/postgres

3. **redis**: Redis cache
   - Port: 6379
   - Data persistence: redis_data volume

## Package Management with uv

This project uses the `uv` package manager instead of `pip` for faster and more reliable Python package management. The Dockerfile and Makefile are configured to use `uv` for installing dependencies from `pyproject.toml`.

## Database Initialization

The database is automatically initialized when the containers start for the first time. The initialization process:

1. Creates the PostgreSQL database
2. Runs any SQL scripts in the docker/postgres/init-db.sh file
3. Runs Alembic migrations
4. Creates all tables defined in SQLAlchemy models

## Creating an Admin User

After setting up the application, you can create an admin user:

```bash
make create-admin
```

## Troubleshooting

If you encounter issues with the database initialization:

1. Check the logs: `make logs`
2. Reset the database: `make db-reset`
3. Manually initialize the database: `make db-init`