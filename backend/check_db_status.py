from database import engine, User, Strategy, Trade, ExchangeAccount
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()
print('数据库表:', tables)

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
db = Session()

print(f'Users count: {db.query(User).count()}')
print(f'Strategies count: {db.query(Strategy).count()}') 
print(f'Trades count: {db.query(Trade).count()}')
print(f'ExchangeAccounts count: {db.query(ExchangeAccount).count()}')

# 检查ExchangeAccount表结构
print('ExchangeAccount表结构:')
for column in inspector.get_columns('exchange_accounts'):
    print(f'  {column["name"]}: {column["type"]}')

db.close()
