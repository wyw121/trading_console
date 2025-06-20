#!/usr/bin/env python3
"""
检查数据库表结构
"""
import sqlite3

def check_database_schema():
    try:
        conn = sqlite3.connect('trading_console_dev.db')
        cursor = conn.cursor()
        
        # 检查 exchange_accounts 表结构
        cursor.execute("PRAGMA table_info(exchange_accounts)")
        columns = cursor.fetchall()
        
        print("Exchange accounts table schema:")
        for col in columns:
            print(f"  {col}")
        
        conn.close()
        return columns
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    check_database_schema()
