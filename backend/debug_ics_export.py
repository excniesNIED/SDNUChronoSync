#!/usr/bin/env python3
"""
ICS导出问题诊断脚本
用于检查为什么数据库中的课程没有出现在ICS导出中
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db
from models import User, Schedule, Event
from utils import parse_weeks, parse_period_to_class_numbers
from datetime import datetime, timedelta

def diagnose_ics_export_issues():
    """诊断ICS导出问题"""
    db = next(get_db())
    
    print("=== ICS导出问题诊断 ===\n")
    
    # 1. 检查数据库中的基本数据
    users = db.query(User).all()
    schedules = db.query(Schedule).all()
    events = db.query(Event).all()
    
    print(f"数据库统计:")
    print(f"  用户总数: {len(users)}")
    print(f"  课表总数: {len(schedules)}")
    print(f"  事件总数: {len(events)}")
    print()
    
    # 2. 检查每个课表的事件分布
    print("课表和事件分布:")
    for schedule in schedules:
        event_count = db.query(Event).filter(Event.schedule_id == schedule.id).count()
        print(f"  课表 {schedule.id} '{schedule.name}' (用户: {schedule.owner.full_name}): {event_count} 个事件")
    print()
    
    # 3. 检查可能有问题的事件
    print("事件数据质量检查:")
    problematic_events = []
    
    for event in events:
        issues = []
        
        # 检查基本字段
        if not event.title:
            issues.append("缺少标题")
        if not event.start_time:
            issues.append("缺少开始时间")
        if not event.end_time:
            issues.append("缺少结束时间")
        if not event.schedule_id:
            issues.append("缺少课表ID")
            
        # 检查周数信息
        weeks_input = event.weeks_input or event.weeks_display or ""
        parsed_weeks = parse_weeks(weeks_input)
        if not parsed_weeks and weeks_input:
            issues.append(f"周数解析失败: '{weeks_input}'")
        
        # 检查节次信息
        if event.period:
            period_numbers = parse_period_to_class_numbers(event.period)
            if not period_numbers:
                issues.append(f"节次解析失败: '{event.period}'")
        
        # 检查星期几
        if event.day_of_week is not None and (event.day_of_week < 1 or event.day_of_week > 7):
            issues.append(f"无效的星期几: {event.day_of_week}")
        
        if issues:
            problematic_events.append((event, issues))
            print(f"  ❌ 事件 {event.id} '{event.title}': {', '.join(issues)}")
    
    if not problematic_events:
        print("  ✅ 所有事件数据看起来正常")
    print()
    
    # 4. 模拟ICS导出过程
    print("模拟ICS导出过程:")
    for schedule in schedules:
        print(f"\n--- 课表 {schedule.id} '{schedule.name}' ---")
        events_in_schedule = db.query(Event).filter(Event.schedule_id == schedule.id).all()
        print(f"查询到 {len(events_in_schedule)} 个事件")
        
        if not events_in_schedule:
            print("  ⚠️  没有找到任何事件，检查以下可能原因：")
            
            # 检查是否有事件的schedule_id为NULL
            orphaned_events = db.query(Event).filter(Event.schedule_id.is_(None)).all()
            if orphaned_events:
                print(f"    - 发现 {len(orphaned_events)} 个没有关联课表的事件")
                for e in orphaned_events[:3]:
                    print(f"      事件 {e.id}: '{e.title}'")
            
            # 检查是否有事件关联到错误的schedule_id
            all_schedule_ids = [s.id for s in schedules]
            mislinked_events = db.query(Event).filter(~Event.schedule_id.in_(all_schedule_ids)).all()
            if mislinked_events:
                print(f"    - 发现 {len(mislinked_events)} 个关联到不存在课表的事件")
                for e in mislinked_events[:3]:
                    print(f"      事件 {e.id}: '{e.title}' -> 课表ID {e.schedule_id}")
            
            continue
        
        # 模拟处理每个事件
        successful_events = 0
        failed_events = 0
        
        for event in events_in_schedule:
            try:
                # 模拟周数解析
                weeks = parse_weeks(event.weeks_input or event.weeks_display or "")
                if not weeks:
                    weeks = [1]
                
                # 模拟节次解析
                period_numbers = parse_period_to_class_numbers(event.period or "")
                
                # 模拟时间处理
                if period_numbers and schedule.class_times:
                    first_period = str(period_numbers[0])
                    last_period = str(period_numbers[-1])
                    
                    if first_period in schedule.class_times and last_period in schedule.class_times:
                        start_time_str = schedule.class_times[first_period].get("start", "08:00")
                        end_time_str = schedule.class_times[last_period].get("end", "09:00")
                    else:
                        start_time_str = event.start_time.strftime("%H:%M")
                        end_time_str = event.end_time.strftime("%H:%M")
                else:
                    start_time_str = event.start_time.strftime("%H:%M")
                    end_time_str = event.end_time.strftime("%H:%M")
                
                # 模拟时间格式解析
                start_hour, start_minute = map(int, start_time_str.split(':'))
                end_hour, end_minute = map(int, end_time_str.split(':'))
                
                # 模拟日期计算
                for week_num in weeks:
                    if event.day_of_week:
                        days_from_start = (week_num - 1) * 7 + (event.day_of_week - 1)
                        event_date = schedule.start_date + timedelta(days=days_from_start)
                    else:
                        event_date = event.start_time.date()
                    
                    # 如果能到这里，说明事件处理成功
                    successful_events += 1
                
            except Exception as e:
                failed_events += 1
                print(f"  ❌ 事件 {event.id} '{event.title}' 处理失败: {str(e)}")
        
        print(f"  处理结果: {successful_events} 个成功, {failed_events} 个失败")
    
    print(f"\n=== 诊断完成 ===")
    db.close()

if __name__ == "__main__":
    diagnose_ics_export_issues()

