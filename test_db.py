from app.db.session import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1')).scalar()
        print('Database connection successful:', result)
except Exception as e:
    print('Database connection failed:', str(e))
