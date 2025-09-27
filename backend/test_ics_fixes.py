#!/usr/bin/env python3
"""
测试ICS导出修复效果的脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db
from models import User, Schedule, Event
from utils import parse_weeks, parse_period_to_class_numbers

def test_specific_events():
    """测试特定事件的处理"""
    db = next(get_db())
    
    print("🔍 测试ICS导出修复效果")
    print("=" * 50)
    
    # 查找李小明的用户信息
    user = db.query(User).filter(User.full_name == "李小明").first()
    if not user:
        print("❌ 没有找到李小明用户")
        return
    
    print(f"👤 找到用户: {user.full_name} (ID: {user.id})")
    
    # 查找李小明的课表
    schedules = db.query(Schedule).filter(Schedule.owner_id == user.id).all()
    if not schedules:
        print("❌ 李小明没有课表")
        return
    
    print(f"📅 找到 {len(schedules)} 个课表")
    
    # 测试特定的问题事件
    test_cases = [
        "中国近现代史纲要",
        "健美操(一)",
        "形势与政策"
    ]
    
    for schedule in schedules:
        print(f"\n📋 课表: {schedule.name} (ID: {schedule.id})")
        
        for test_case in test_cases:
            events = db.query(Event).filter(
                Event.schedule_id == schedule.id,
                Event.title.contains(test_case)
            ).all()
            
            if events:
                print(f"\n🔍 测试事件: {test_case}")
                for event in events:
                    print(f"  事件ID: {event.id}")
                    print(f"  标题: {event.title}")
                    print(f"  地点: {event.location}")
                    print(f"  教师: {event.instructor}")
                    print(f"  星期几: {event.day_of_week}")
                    print(f"  节次: {event.period}")
                    print(f"  周数显示: {event.weeks_display}")
                    print(f"  周数输入: {event.weeks_input}")
                    
                    # 测试周数解析
                    weeks_str = event.weeks_input or event.weeks_display or ""
                    weeks = parse_weeks(weeks_str)
                    print(f"  周数字符串: '{weeks_str}'")
                    print(f"  解析后周数: {weeks}")
                    
                    if len(weeks) > 0:
                        print(f"  ✅ 周数解析成功，共 {len(weeks)} 周")
                    else:
                        print(f"  ❌ 周数解析失败！")
                    
                    # 测试节次解析
                    period_numbers = parse_period_to_class_numbers(event.period or "")
                    print(f"  解析后节次: {period_numbers}")
                    
                    # 测试星期几处理
                    if event.day_of_week is not None and event.day_of_week >= 1 and event.day_of_week <= 7:
                        day_names = ["", "周一", "周二", "周三", "周四", "周五", "周六", "周日"]
                        day_name = day_names[event.day_of_week]
                        print(f"  星期几显示: {day_name}")
                        print(f"  ✅ 星期几处理正常")
                    else:
                        print(f"  ❌ 星期几数据异常: {event.day_of_week}")
                    
                    # 测试地点处理
                    if event.location and event.location.strip():
                        print(f"  ✅ 地点信息正常: {event.location}")
                    else:
                        print(f"  ⚠️  地点信息为空，将显示为'未排地点'")
                    
                    print("  " + "-" * 40)
            else:
                print(f"\n❌ 没有找到事件: {test_case}")
    
    # 测试所有"未排地点"的事件
    print(f"\n🔍 查找所有'未排地点'的事件:")
    unplaced_events = db.query(Event).filter(
        Event.schedule_id.in_([s.id for s in schedules]),
        Event.location.contains("未排地点")
    ).all()
    
    if unplaced_events:
        print(f"  找到 {len(unplaced_events)} 个'未排地点'事件:")
        for event in unplaced_events[:5]:  # 只显示前5个
            print(f"    - {event.title} (ID: {event.id})")
    else:
        print("  没有找到'未排地点'事件")
    
    # 测试地点为空或None的事件
    print(f"\n🔍 查找地点为空的事件:")
    empty_location_events = db.query(Event).filter(
        Event.schedule_id.in_([s.id for s in schedules]),
        (Event.location.is_(None)) | (Event.location == "")
    ).all()
    
    if empty_location_events:
        print(f"  找到 {len(empty_location_events)} 个地点为空的事件:")
        for event in empty_location_events[:5]:  # 只显示前5个
            print(f"    - {event.title} (ID: {event.id})")
    else:
        print("  没有找到地点为空的事件")
    
    db.close()
    print(f"\n✅ 测试完成")

if __name__ == "__main__":
    test_specific_events()
