#!/usr/bin/env python3
"""
数据库迁移脚本 - 添加新的Event字段
"""

import sqlite3
import os
from pathlib import Path

def migrate_database():
    """添加新的字段到events表"""
    
    # 数据库文件路径
    db_path = Path(__file__).parent / "schedule_management.db"
    
    if not db_path.exists():
        print("数据库文件不存在，将在首次运行时自动创建")
        return
    
    try:
        # 连接数据库
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 检查是否已经存在新字段
        cursor.execute("PRAGMA table_info(events)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"当前events表的字段: {columns}")
        
        # 需要添加的新字段
        new_columns = [
            ("instructor", "VARCHAR"),
            ("weeks_display", "VARCHAR"), 
            ("day_of_week", "INTEGER"),
            ("period", "VARCHAR")
        ]
        
        # 添加缺失的字段
        for column_name, column_type in new_columns:
            if column_name not in columns:
                try:
                    sql = f"ALTER TABLE events ADD COLUMN {column_name} {column_type}"
                    cursor.execute(sql)
                    print(f"✅ 成功添加字段: {column_name}")
                except sqlite3.Error as e:
                    print(f"❌ 添加字段 {column_name} 失败: {e}")
            else:
                print(f"⏭️  字段 {column_name} 已存在，跳过")
        
        # 提交更改
        conn.commit()
        print("\n🎉 数据库迁移完成！")
        
        # 验证迁移结果
        cursor.execute("PRAGMA table_info(events)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        print(f"迁移后events表的字段: {updated_columns}")
        
    except sqlite3.Error as e:
        print(f"❌ 数据库迁移失败: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("开始数据库迁移...")
    migrate_database()
