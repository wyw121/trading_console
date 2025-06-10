from database import engine
from sqlalchemy import text
import traceback

print("Testing database connection...")

try:
    print("Creating engine connection...")
    with engine.connect() as conn:
        print("Connection established, executing query...")
        result = conn.execute(text('SELECT 1'))
        row = result.fetchone()
        print('Database connection successful:', row)
except Exception as e:
    print('Database connection failed:', str(e))
    print('Full traceback:')
    traceback.print_exc()
