"""
Description: 
    
-*- Encoding: UTF-8 -*-
@File     ：create_database.py
@Author   ：King Songtao
@Time     ：2024/12/16 下午4:27
@Contact  ：king.songtao@gmail.com
"""
import sqlite3


def create_database():
    # 连接 SQLite 数据库（如果没有数据库文件，会自动创建）
    conn = sqlite3.connect('work_orders.db')
    cursor = conn.cursor()

    # 创建工单表格
    cursor.execute('''CREATE TABLE IF NOT EXISTS work_orders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        register_time TEXT,
                        notes TEXT,
                        work_time TEXT,
                        address TEXT,
                        project TEXT,
                        dispatcher TEXT,
                        confirmed TEXT,
                        registered TEXT,
                        dispatched TEXT,
                        dispatch_price REAL,
                        final_price REAL,
                        receipt_or_invoice TEXT,
                        sent_or_not TEXT)''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()
