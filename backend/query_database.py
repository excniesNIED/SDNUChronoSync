#!/usr/bin/env python3
"""
数据库查询工具
用于查看SQLite数据库中的数据内容
"""

import sqlite3
import sys
import os
from datetime import datetime

def connect_to_database(db_path="schedule_app.db"):
    """连接到数据库"""
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # 使结果可以按列名访问
        return conn
    except Exception as e:
        print(f"❌ 连接数据库失败: {e}")
        return None

def show_table_structure(conn, table_name):
    """显示表结构"""
    try:
        cursor = conn.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print(f"\n📋 表 '{table_name}' 的结构:")
        print("列名".ljust(20) + "类型".ljust(15) + "是否为空".ljust(10) + "默认值")
        print("-" * 60)
        
        for col in columns:
            name = col['name']
            type_name = col['type']
            not_null = "NOT NULL" if col['notnull'] else "NULL"
            default_value = col['dflt_value'] or ""
            print(f"{name:<20} {type_name:<15} {not_null:<10} {default_value}")
            
    except Exception as e:
        print(f"❌ 获取表结构失败: {e}")

def query_users(conn):
    """查询用户数据"""
    print("\n👥 用户数据:")
    try:
        cursor = conn.execute("""
            SELECT id, student_id, full_name, class_name, grade, role, created_at 
            FROM users 
            ORDER BY id
        """)
        users = cursor.fetchall()
        
        if not users:
            print("  📭 没有找到用户数据")
            return
        
        print("ID".ljust(5) + "学号".ljust(15) + "姓名".ljust(10) + "班级".ljust(15) + "年级".ljust(8) + "角色".ljust(8) + "创建时间")
        print("-" * 80)
        
        for user in users:
            created_at = user['created_at'][:19] if user['created_at'] else ""
            print(f"{user['id']:<5} {user['student_id']:<15} {user['full_name']:<10} {user['class_name']:<15} {user['grade']:<8} {user['role']:<8} {created_at}")
            
    except Exception as e:
        print(f"❌ 查询用户数据失败: {e}")

def query_schedules(conn):
    """查询课表数据"""
    print("\n📅 课表数据:")
    try:
        cursor = conn.execute("""
            SELECT s.id, s.name, s.owner_id, u.full_name as owner_name, 
                   s.status, s.start_date, s.total_weeks, s.created_at
            FROM schedules s
            LEFT JOIN users u ON s.owner_id = u.id
            ORDER BY s.id
        """)
        schedules = cursor.fetchall()
        
        if not schedules:
            print("  📭 没有找到课表数据")
            return
        
        print("ID".ljust(5) + "课表名".ljust(20) + "拥有者".ljust(12) + "状态".ljust(8) + "开始日期".ljust(12) + "周数".ljust(6) + "创建时间")
        print("-" * 85)
        
        for schedule in schedules:
            created_at = schedule['created_at'][:19] if schedule['created_at'] else ""
            owner_name = schedule['owner_name'] or f"ID:{schedule['owner_id']}"
            print(f"{schedule['id']:<5} {schedule['name']:<20} {owner_name:<12} {schedule['status']:<8} {schedule['start_date']:<12} {schedule['total_weeks']:<6} {created_at}")
            
    except Exception as e:
        print(f"❌ 查询课表数据失败: {e}")

def query_events(conn, schedule_id=None, limit=50):
    """查询事件数据"""
    print(f"\n📝 事件数据 (限制显示前{limit}条):")
    try:
        if schedule_id:
            query = """
                SELECT e.id, e.schedule_id, s.name as schedule_name, e.title, 
                       e.location, e.instructor, e.weeks_display, e.weeks_input,
                       e.day_of_week, e.period, e.start_time, e.end_time
                FROM events e
                LEFT JOIN schedules s ON e.schedule_id = s.id
                WHERE e.schedule_id = ?
                ORDER BY e.id
                LIMIT ?
            """
            cursor = conn.execute(query, (schedule_id, limit))
        else:
            query = """
                SELECT e.id, e.schedule_id, s.name as schedule_name, e.title, 
                       e.location, e.instructor, e.weeks_display, e.weeks_input,
                       e.day_of_week, e.period, e.start_time, e.end_time
                FROM events e
                LEFT JOIN schedules s ON e.schedule_id = s.id
                ORDER BY e.id
                LIMIT ?
            """
            cursor = conn.execute(query, (limit,))
            
        events = cursor.fetchall()
        
        if not events:
            print("  📭 没有找到事件数据")
            return
        
        print("ID".ljust(5) + "课表ID".ljust(8) + "课程名".ljust(25) + "地点".ljust(15) + "教师".ljust(12) + "周数".ljust(15) + "星期".ljust(6) + "节次")
        print("-" * 100)
        
        for event in events:
            schedule_name = event['schedule_name'] or f"ID:{event['schedule_id']}"
            location = (event['location'] or "")[:14]
            instructor = (event['instructor'] or "")[:11]
            weeks = (event['weeks_display'] or event['weeks_input'] or "")[:14]
            day_name = ["", "周一", "周二", "周三", "周四", "周五", "周六", "周日"][event['day_of_week']] if event['day_of_week'] else ""
            period = event['period'] or ""
            
            print(f"{event['id']:<5} {event['schedule_id']:<8} {event['title'][:24]:<25} {location:<15} {instructor:<12} {weeks:<15} {day_name:<6} {period}")
            
    except Exception as e:
        print(f"❌ 查询事件数据失败: {e}")

def query_events_by_schedule(conn):
    """按课表分组显示事件统计"""
    print("\n📊 各课表的事件统计:")
    try:
        cursor = conn.execute("""
            SELECT s.id, s.name, s.owner_id, u.full_name as owner_name,
                   COUNT(e.id) as event_count
            FROM schedules s
            LEFT JOIN users u ON s.owner_id = u.id
            LEFT JOIN events e ON s.id = e.schedule_id
            GROUP BY s.id, s.name, s.owner_id, u.full_name
            ORDER BY s.id
        """)
        results = cursor.fetchall()
        
        if not results:
            print("  📭 没有找到数据")
            return
        
        print("课表ID".ljust(8) + "课表名".ljust(20) + "拥有者".ljust(12) + "事件数量")
        print("-" * 50)
        
        total_events = 0
        for result in results:
            owner_name = result['owner_name'] or f"ID:{result['owner_id']}"
            event_count = result['event_count']
            total_events += event_count
            print(f"{result['id']:<8} {result['name']:<20} {owner_name:<12} {event_count}")
        
        print(f"\n总计: {total_events} 个事件")
            
    except Exception as e:
        print(f"❌ 查询统计数据失败: {e}")

def check_orphaned_events(conn):
    """检查孤立的事件（没有关联课表的事件）"""
    print("\n🔍 检查孤立事件:")
    try:
        cursor = conn.execute("""
            SELECT e.id, e.title, e.schedule_id, e.start_time, e.end_time
            FROM events e
            LEFT JOIN schedules s ON e.schedule_id = s.id
            WHERE s.id IS NULL OR e.schedule_id IS NULL
            ORDER BY e.id
        """)
        orphaned_events = cursor.fetchall()
        
        if not orphaned_events:
            print("  ✅ 没有发现孤立事件")
            return
        
        print(f"  ⚠️  发现 {len(orphaned_events)} 个孤立事件:")
        print("事件ID".ljust(8) + "标题".ljust(30) + "关联课表ID".ljust(12) + "开始时间")
        print("-" * 60)
        
        for event in orphaned_events:
            schedule_id = event['schedule_id'] or "NULL"
            start_time = event['start_time'][:19] if event['start_time'] else ""
            print(f"{event['id']:<8} {event['title'][:29]:<30} {schedule_id:<12} {start_time}")
            
    except Exception as e:
        print(f"❌ 检查孤立事件失败: {e}")

def query_user_schedules(conn, user_name):
    """查询指定用户的所有课表和事件数据"""
    print(f"\n👤 查询用户 '{user_name}' 的所有数据:")
    
    try:
        # 首先查找用户
        cursor = conn.execute("""
            SELECT id, student_id, full_name, class_name, grade, role
            FROM users 
            WHERE full_name = ? OR student_id = ?
        """, (user_name, user_name))
        
        users = cursor.fetchall()
        
        if not users:
            print(f"  ❌ 没有找到用户: {user_name}")
            return
        
        for user in users:
            print(f"\n📋 用户信息:")
            print(f"  ID: {user['id']}")
            print(f"  学号: {user['student_id']}")
            print(f"  姓名: {user['full_name']}")
            print(f"  班级: {user['class_name']}")
            print(f"  年级: {user['grade']}")
            print(f"  角色: {user['role']}")
            
            # 查询该用户的所有课表
            cursor = conn.execute("""
                SELECT id, name, status, start_date, total_weeks, created_at, class_times
                FROM schedules 
                WHERE owner_id = ?
                ORDER BY id
            """, (user['id'],))
            
            schedules = cursor.fetchall()
            
            if not schedules:
                print(f"\n  📭 用户 {user['full_name']} 没有课表")
                continue
            
            print(f"\n📅 课表列表 ({len(schedules)} 个):")
            print("ID".ljust(5) + "课表名".ljust(25) + "状态".ljust(8) + "开始日期".ljust(12) + "周数".ljust(6) + "创建时间")
            print("-" * 70)
            
            for schedule in schedules:
                created_at = schedule['created_at'][:19] if schedule['created_at'] else ""
                print(f"{schedule['id']:<5} {schedule['name']:<25} {schedule['status']:<8} {schedule['start_date']:<12} {schedule['total_weeks']:<6} {created_at}")
            
            # 查询每个课表的详细事件
            for schedule in schedules:
                print(f"\n📝 课表 '{schedule['name']}' (ID: {schedule['id']}) 的事件:")
                
                cursor = conn.execute("""
                    SELECT id, title, location, instructor, weeks_display, weeks_input,
                           day_of_week, period, start_time, end_time, description, color
                    FROM events 
                    WHERE schedule_id = ?
                    ORDER BY day_of_week, period, title
                """, (schedule['id'],))
                
                events = cursor.fetchall()
                
                if not events:
                    print("  📭 该课表没有事件")
                    continue
                
                print(f"  共 {len(events)} 个事件:")
                print("  ID".ljust(6) + "课程名".ljust(25) + "地点".ljust(15) + "教师".ljust(12) + "时间".ljust(20) + "周数")
                print("  " + "-" * 85)
                
                for event in events:
                    location = (event['location'] or "")[:14]
                    instructor = (event['instructor'] or "")[:11]
                    weeks = (event['weeks_display'] or event['weeks_input'] or "")[:14]
                    
                    # 格式化时间信息
                    day_names = ["", "周一", "周二", "周三", "周四", "周五", "周六", "周日"]
                    day_name = day_names[event['day_of_week']] if event['day_of_week'] and event['day_of_week'] <= 7 else ""
                    period = event['period'] or ""
                    time_info = f"{day_name} {period}".strip()[:19]
                    
                    print(f"  {event['id']:<6} {event['title'][:24]:<25} {location:<15} {instructor:<12} {time_info:<20} {weeks}")
                    
                    # 如果有描述，显示描述
                    if event['description'] and event['description'].strip():
                        print(f"    📄 描述: {event['description'][:50]}...")
                
                print()  # 课表间的空行
    
    except Exception as e:
        print(f"❌ 查询用户数据失败: {e}")

def main():
    """主函数"""
    print("🔍 SDNUChronoSync 数据库查询工具")
    print("=" * 50)
    
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        # 检查命令行参数
        if len(sys.argv) > 1:
            arg = sys.argv[1]
            
            # 检查是否是查询特定用户
            if arg in ["李小明", "lixiaoming"] or "李小明" in arg:
                query_user_schedules(conn, "李小明")
                return
            
            # 检查是否是数字（课表ID）
            try:
                schedule_id = int(arg)
                print(f"\n🔎 课表 {schedule_id} 的详细事件:")
                query_events(conn, schedule_id, 100)
                return
            except ValueError:
                # 尝试作为用户名查询
                query_user_schedules(conn, arg)
                return
        
        # 默认显示所有数据的概览
        # 显示基本统计信息
        cursor = conn.execute("SELECT COUNT(*) as count FROM users")
        user_count = cursor.fetchone()['count']
        
        cursor = conn.execute("SELECT COUNT(*) as count FROM schedules")
        schedule_count = cursor.fetchone()['count']
        
        cursor = conn.execute("SELECT COUNT(*) as count FROM events")
        event_count = cursor.fetchone()['count']
        
        print(f"\n📈 数据库统计:")
        print(f"  用户数量: {user_count}")
        print(f"  课表数量: {schedule_count}")
        print(f"  事件数量: {event_count}")
        
        # 查询各表数据
        query_users(conn)
        query_schedules(conn)
        query_events_by_schedule(conn)
        query_events(conn, limit=20)  # 只显示前20个事件
        check_orphaned_events(conn)
        
        print(f"\n💡 使用提示:")
        print(f"  python query_database.py 李小明     # 查看李小明的所有数据")
        print(f"  python query_database.py 1         # 查看课表ID为1的详细事件")
        print(f"  python query_database.py 用户名     # 查看指定用户的所有数据")
        
    except Exception as e:
        print(f"❌ 查询过程中发生错误: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
