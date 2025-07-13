from app.db.base import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'users'"))
    columns = [row[0] for row in result.fetchall()]
    print("Columns in users table:", columns)