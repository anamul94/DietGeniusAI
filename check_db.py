from app.db.base import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
    tables = [row[0] for row in result.fetchall()]
    print("Tables:", tables)