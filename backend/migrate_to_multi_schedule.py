#!/usr/bin/env python3
"""
数据库迁移脚本 - 从单一事件模式迁移到多课表模式
"""

import sqlite3
import os
from pathlib import Path
from datetime import date, datetime
import json

from utils import get_default_class_times


def migrate_database():
    """将数据库从单一事件模式迁移到多课表模式"""
    
    # 数据库文件路径
    db_path = Path(__file__).parent / "schedule_app.db"
    backup_path = Path(__file__).parent / "schedule_app_backup.db"
    
    if not db_path.exists():
        print("数据库文件不存在，将在首次运行时自动创建")
        return
    
    print("开始数据库迁移...")
    
    try:
        # 备份原始数据库
        import shutil
        shutil.copy2(str(db_path), str(backup_path))
        print(f"✅ 已备份原数据库到: {backup_path}")
        
        # 连接数据库
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 检查是否已经存在schedules表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schedules'")
        if cursor.fetchone():
            print("⏭️  schedules表已存在，迁移可能已完成")
            conn.close()
            return
        
        print("开始创建新的表结构...")
        
        # 1. 创建schedules表
        cursor.execute("""
            CREATE TABLE schedules (
                id INTEGER PRIMARY KEY,
                name VARCHAR NOT NULL,
                owner_id INTEGER NOT NULL,
                status VARCHAR DEFAULT '进行',
                start_date DATE NOT NULL,
                total_weeks INTEGER DEFAULT 20,
                class_times JSON NOT NULL,
                created_at DATETIME,
                updated_at DATETIME,
                FOREIGN KEY (owner_id) REFERENCES users(id)
            )
        """)
        print("✅ 创建schedules表成功")
        
        # 2. 获取所有用户
        cursor.execute("SELECT id, student_id, full_name FROM users")
        users = cursor.fetchall()
        
        # 3. 为每个用户创建默认课表
        default_class_times = json.dumps(get_default_class_times())
        current_time = datetime.now()
        default_start_date = '2024-09-01'  # 默认开学日期
        
        for user_id, student_id, full_name in users:
            schedule_name = f"{full_name}的课表"
            cursor.execute("""
                INSERT INTO schedules (name, owner_id, status, start_date, total_weeks, class_times, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (schedule_name, user_id, '进行', default_start_date, 20, default_class_times, current_time, current_time))
            
            print(f"✅ 为用户 {full_name} 创建默认课表")
        
        # 4. 备份原events表数据
        cursor.execute("SELECT * FROM events")
        old_events = cursor.fetchall()
        
        # 获取events表的列信息
        cursor.execute("PRAGMA table_info(events)")
        columns_info = cursor.fetchall()
        columns = [col[1] for col in columns_info]
        
        print(f"📊 找到 {len(old_events)} 个原始事件")
        
        # 5. 创建新的events表
        cursor.execute("ALTER TABLE events RENAME TO events_old")
        
        cursor.execute("""
            CREATE TABLE events (
                id INTEGER PRIMARY KEY,
                schedule_id INTEGER NOT NULL,
                title VARCHAR NOT NULL,
                description TEXT,
                location VARCHAR,
                start_time DATETIME NOT NULL,
                end_time DATETIME NOT NULL,
                created_at DATETIME,
                updated_at DATETIME,
                instructor VARCHAR,
                weeks_display VARCHAR,
                day_of_week INTEGER,
                period VARCHAR,
                weeks_input VARCHAR,
                FOREIGN KEY (schedule_id) REFERENCES schedules(id)
            )
        """)
        print("✅ 创建新的events表成功")
        
        # 6. 迁移事件数据
        if old_events:
            # 获取用户的默认课表ID映射
            cursor.execute("SELECT owner_id, id FROM schedules")
            user_schedule_map = dict(cursor.fetchall())
            
            migrated_count = 0
            for event_data in old_events:
                event_dict = dict(zip(columns, event_data))
                
                # 获取用户的默认课表ID
                owner_id = event_dict.get('owner_id')
                if owner_id and owner_id in user_schedule_map:
                    schedule_id = user_schedule_map[owner_id]
                    
                    # 插入到新events表
                    cursor.execute("""
                        INSERT INTO events 
                        (schedule_id, title, description, location, start_time, end_time, 
                         created_at, updated_at, instructor, weeks_display, day_of_week, period, weeks_input)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        schedule_id,
                        event_dict.get('title'),
                        event_dict.get('description'),
                        event_dict.get('location'),
                        event_dict.get('start_time'),
                        event_dict.get('end_time'),
                        event_dict.get('created_at'),
                        event_dict.get('updated_at'),
                        event_dict.get('instructor'),
                        event_dict.get('weeks_display'),
                        event_dict.get('day_of_week'),
                        event_dict.get('period'),
                        event_dict.get('weeks_display')  # 将weeks_display复制为weeks_input
                    ))
                    migrated_count += 1
            
            print(f"✅ 迁移了 {migrated_count} 个事件到新表结构")
        
        # 7. 删除旧表
        cursor.execute("DROP TABLE events_old")
        print("✅ 删除旧events表")
        
        # 提交更改
        conn.commit()
        print("\n🎉 数据库迁移完成！")
        
        # 验证迁移结果
        cursor.execute("SELECT COUNT(*) FROM schedules")
        schedule_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM events")
        event_count = cursor.fetchone()[0]
        
        print(f"📊 迁移结果统计:")
        print(f"   - 课表数量: {schedule_count}")
        print(f"   - 事件数量: {event_count}")
        
    except Exception as e:
        print(f"❌ 数据库迁移失败: {e}")
        if conn:
            conn.rollback()
        
        # 如果迁移失败，恢复备份
        try:
            if backup_path.exists():
                shutil.copy2(str(backup_path), str(db_path))
                print(f"🔄 已从备份恢复数据库")
        except Exception as restore_error:
            print(f"❌ 恢复备份失败: {restore_error}")
        
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    print("开始数据库迁移到多课表架构...")
    migrate_database()
    print("迁移完成！请重启后端服务以使用新的表结构。")
