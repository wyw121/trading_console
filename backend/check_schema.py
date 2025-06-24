from database import SessionLocal, ExchangeAccount
import sqlalchemy as sa

with SessionLocal() as db:
    inspector = sa.inspect(db.bind)
    columns = inspector.get_columns('exchange_accounts')
    print('ExchangeAccount表字段:')
    for col in columns:
        print(f'  {col["name"]}: {col["type"]}')
