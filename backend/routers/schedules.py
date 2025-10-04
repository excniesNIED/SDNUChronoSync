from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Union
from datetime import date, datetime, timedelta
import ics

from database import get_db
from auth import get_current_user, get_current_admin_user
from models import User, Schedule, Event, ScheduleAdjustment
from schemas import (
    ScheduleCreate, ScheduleUpdate, ScheduleResponse, EventCreate, EventUpdate, EventResponse,
    HolidayAdjustmentRequest, SwapAdjustmentRequest, AdjustmentOperationResponse, ScheduleAdjustmentResponse
)
from utils import get_default_class_times, parse_weeks, parse_period_to_class_numbers
import crud

router = APIRouter(prefix="/api/schedules", tags=["schedules"])


@router.get("/", response_model=List[ScheduleResponse])
async def get_user_schedules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的所有课表"""
    schedules = db.query(Schedule).filter(Schedule.owner_id == current_user.id).all()
    return schedules


@router.post("/", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule_data: ScheduleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新课表"""
    
    # 创建课表对象
    db_schedule = Schedule(
        name=schedule_data.name,
        owner_id=current_user.id,
        status=schedule_data.status,
        start_date=schedule_data.start_date,
        total_weeks=schedule_data.total_weeks,
        class_times=schedule_data.class_times if schedule_data.class_times else get_default_class_times()
    )
    
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    
    return db_schedule


@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取指定课表"""
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.owner_id == current_user.id
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    return schedule


@router.put("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int,
    schedule_data: ScheduleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新指定课表"""
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.owner_id == current_user.id
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    # 更新字段
    update_data = schedule_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(schedule, field, value)
    
    db.commit()
    db.refresh(schedule)
    
    return schedule


@router.delete("/{schedule_id}")
async def delete_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除指定课表"""
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.owner_id == current_user.id
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    db.delete(schedule)
    db.commit()
    
    return {"message": "Schedule deleted successfully"}


@router.get("/{schedule_id}/events", response_model=List[EventResponse])
async def get_schedule_events(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10000
):
    """获取指定课表的所有事件"""
    # 验证课表所有权
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.owner_id == current_user.id
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    events = (
        db.query(Event)
        .filter(
            Event.schedule_id == schedule_id,
            Event.is_active == True  # 只返回活跃的事件
        )
        .order_by(Event.start_time.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return events


@router.post("/{schedule_id}/events", response_model=List[EventResponse], status_code=status.HTTP_201_CREATED)
async def create_schedule_event(
    schedule_id: int,
    event_data: EventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """在指定课表下创建事件，支持周数范围"""
    # 验证课表所有权
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.owner_id == current_user.id
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    # 使用新的递归事件创建函数
    created_events = crud.create_recurring_event(db, event_data, schedule_id)
    
    return created_events


@router.put("/{schedule_id}/events/{event_id}", response_model=EventResponse)
async def update_schedule_event(
    schedule_id: int,
    event_id: int,
    event_data: EventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新指定课表的事件"""
    # 验证课表所有权
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.owner_id == current_user.id
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    # 获取事件
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.schedule_id == schedule_id
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # 更新事件
    update_data = event_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
    
    return event


@router.delete("/{schedule_id}/events/{event_id}")
async def delete_schedule_event(
    schedule_id: int,
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除指定课表的事件"""
    # 验证课表所有权
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.owner_id == current_user.id
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    # 获取事件
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.schedule_id == schedule_id
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    db.delete(event)
    db.commit()
    
    return {"message": "Event deleted successfully"}


@router.get("/{schedule_id}/export.ics")
async def export_schedule_to_ics(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """导出指定课表为ICS文件"""
    # 验证课表所有权
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.owner_id == current_user.id
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    # 获取所有事件（确保有序，防止结果顺序不稳定）
    events = (
        db.query(Event)
        .filter(Event.schedule_id == schedule_id)
        .order_by(Event.day_of_week, Event.period, Event.start_time)
        .all()
    )
    
    print(f"\n=== ICS导出调试信息 ===")
    print(f"当前用户ID: {current_user.id} ({current_user.full_name})")
    print(f"请求导出的课表ID: {schedule_id}")
    print(f"课表名称: {schedule.name}")
    print(f"课表拥有者ID: {schedule.owner_id}")
    print(f"课表开始日期: {schedule.start_date}")
    print(f"课表状态: {schedule.status}")
    print(f"查询条件: Event.schedule_id == {schedule_id}")
    print(f"找到事件数量: {len(events)}")
    
    # 如果没有找到事件，进一步调试
    if len(events) == 0:
        print("\n⚠️  警告：没有找到任何事件！")
        # 检查用户的所有课表
        user_schedules = db.query(Schedule).filter(Schedule.owner_id == current_user.id).all()
        print(f"用户拥有的课表数量: {len(user_schedules)}")
        for s in user_schedules:
            event_count = db.query(Event).filter(Event.schedule_id == s.id).count()
            print(f"  课表ID {s.id} '{s.name}': {event_count} 个事件")
    else:
        # 显示前几个事件的基本信息
        print(f"\n前3个事件概览:")
        for i, event in enumerate(events[:3]):
            print(f"  {i+1}. {event.title} - {event.start_time} (事件ID: {event.id})")
    
    # 创建日历对象
    calendar = ics.Calendar()
    calendar.creator = f"Schedule Management System - {schedule.name}"
    
    # 遍历每个事件
    successful_events = 0
    failed_events = 0
    
    for i, event in enumerate(events):
        try:
            print(f"\n>>> 处理第 {i+1} 个事件: {event.title}")
            print(f"    事件ID: {event.id}")
            print(f"    周数输入: {event.weeks_input}")
            print(f"    周数显示: {event.weeks_display}")
            print(f"    星期几: {event.day_of_week}")
            print(f"    节次: {event.period}")
            print(f"    地点: {event.location}")
            print(f"    教师: {event.instructor}")
            print(f"    原始开始时间: {event.start_time}")
            print(f"    原始结束时间: {event.end_time}")
            
            # 解析周数
            weeks = parse_weeks(event.weeks_input or event.weeks_display or "")
            if not weeks:
                # 如果没有周数信息，创建单次事件
                weeks = [1]
                print(f"    ⚠️  周数信息为空，使用默认周数: [1]")
            
            print(f"    解析后周数: {weeks}")
            
            # 解析节次获取时间
            period_numbers = parse_period_to_class_numbers(event.period or "")
            print(f"    解析后节次: {period_numbers}")
            
            # 获取开始和结束时间
            if period_numbers and schedule.class_times:
                first_period = str(period_numbers[0])
                last_period = str(period_numbers[-1])
                
                print(f"    查找时间 - 第一节: {first_period}, 最后一节: {last_period}")
                print(f"    课表时间配置: {schedule.class_times}")
                
                if first_period in schedule.class_times and last_period in schedule.class_times:
                    start_time_str = schedule.class_times[first_period].get("start", "08:00")
                    end_time_str = schedule.class_times[last_period].get("end", "09:00")
                    print(f"    使用课表时间: {start_time_str} - {end_time_str}")
                else:
                    # 使用事件原始时间
                    start_time_str = event.start_time.strftime("%H:%M")
                    end_time_str = event.end_time.strftime("%H:%M")
                    print(f"    使用事件原始时间: {start_time_str} - {end_time_str}")
            else:
                # 使用事件原始时间
                start_time_str = event.start_time.strftime("%H:%M")
                end_time_str = event.end_time.strftime("%H:%M")
                print(f"    使用事件原始时间(无节次信息): {start_time_str} - {end_time_str}")
            
            # 为每个周数创建ICS事件
            for week_num in weeks:
                # 防止 week_num 无效
                if week_num < 1 or week_num > 60:
                    print(f"    ⚠️  无效的周数 {week_num}，跳过")
                    continue
                
                try:
                    # 计算具体日期
                    if event.day_of_week is not None:
                        day_of_week = event.day_of_week
                        if day_of_week == 0:
                            # 如果存储为0，视为周日（7）
                            day_of_week = 7
                        if day_of_week < 1 or day_of_week > 7:
                            raise ValueError(f"day_of_week 无效: {event.day_of_week}")
                        # 基于星期几计算日期（周一=1 -> offset=0, 周日=7 -> offset=6）
                        day_offset = day_of_week - 1
                        days_from_start = (week_num - 1) * 7 + day_offset
                        event_date = schedule.start_date + timedelta(days=days_from_start)
                        print(f"    第 {week_num} 周 - 星期 {day_of_week} - 计算日期: {event_date}")
                    else:
                        # 使用原始事件日期
                        event_date = event.start_time.date()
                        print(f"    第 {week_num} 周 - 使用原始日期: {event_date} (day_of_week=None)")
                        day_of_week = event.start_time.weekday() + 1  # Python: Monday=0
                    
                    # 生成 ICS 的星期几（周日=SU）
                    weekday_map = {1: 'MO', 2: 'TU', 3: 'WE', 4: 'TH', 5: 'FR', 6: 'SA', 7: 'SU'}
                    ics_weekday = weekday_map.get(day_of_week, 'MO')
                    
                    # 创建开始和结束时间
                    start_hour, start_minute = map(int, start_time_str.split(':'))
                    end_hour, end_minute = map(int, end_time_str.split(':'))
                    
                    start_datetime = datetime.combine(event_date, datetime.min.time().replace(
                        hour=start_hour, minute=start_minute
                    ))
                    end_datetime = datetime.combine(event_date, datetime.min.time().replace(
                        hour=end_hour, minute=end_minute
                    ))
                    
                    print(f"    创建ICS事件: {start_datetime} 到 {end_datetime}")
                    
                    # 创建ICS事件
                    ics_event = ics.Event()
                    ics_event.name = event.title
                    ics_event.begin = start_datetime
                    ics_event.end = end_datetime
                    
                    # 设置位置和描述
                    location_parts = []
                    description_parts = []
                    
                    # 处理地点信息 - 即使是"未排地点"也要显示
                    if event.location and event.location.strip():
                        location_parts.append(event.location.strip())
                        description_parts.append(f"地点: {event.location.strip()}")
                    else:
                        location_parts.append("未排地点")
                        description_parts.append("地点: 未排地点")
                    
                    # 处理教师信息
                    if event.instructor and event.instructor.strip():
                        description_parts.append(f"教师: {event.instructor.strip()}")
                    
                    # 处理周数信息
                    if event.weeks_display or event.weeks_input:
                        weeks_info = (event.weeks_display or event.weeks_input).strip()
                        if weeks_info:
                            description_parts.append(f"周数: {weeks_info}")
                    
                    # 处理节次信息
                    if event.period and event.period.strip():
                        description_parts.append(f"节次: {event.period.strip()}")
                    
                    # 设置ICS事件的位置和描述
                    ics_event.location = "|".join(location_parts)
                    ics_event.description = " | ".join(description_parts)
                    
                    # 添加提醒（提前10分钟）
                    ics_event.alarms = [ics.DisplayAlarm(trigger=timedelta(minutes=-10))]
                    
                    # 生成唯一ID - 使用更安全的格式
                    import hashlib
                    uid_source = f"{schedule_id}-{event.id}-{week_num}-{start_datetime.isoformat()}"
                    uid_hash = hashlib.md5(uid_source.encode()).hexdigest()[:8]
                    ics_event.uid = f"event-{schedule_id}-{event.id}-w{week_num}-{uid_hash}@chronosync"
                    
                    calendar.events.add(ics_event)
                    successful_events += 1
                    
                except Exception as week_error:
                    print(f"    ❌ 第 {week_num} 周处理失败: {str(week_error)}")
                    failed_events += 1
                    continue
            
        except Exception as event_error:
            print(f"    ❌ 事件 {event.id} '{event.title}' 处理失败: {str(event_error)}")
            failed_events += 1
            continue
    
    print(f"\n=== ICS导出完成 ===")
    print(f"成功处理: {successful_events} 个事件")
    print(f"处理失败: {failed_events} 个事件")
    print(f"总共创建了 {len(calendar.events)} 个ICS事件")
    
    # 生成ICS内容
    ics_content = str(calendar)
    
    # 设置响应头
    filename = f"{schedule.name.replace(' ', '_')}.ics"
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"',
        'Content-Type': 'text/calendar; charset=utf-8'
    }
    
    return Response(content=ics_content, headers=headers)


@router.post("/{schedule_id}/adjustments", response_model=AdjustmentOperationResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule_adjustment(
    schedule_id: int,
    adjustment_data: Union[HolidayAdjustmentRequest, SwapAdjustmentRequest],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建课表调休调整"""
    # 验证课表所有权
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.owner_id == current_user.id
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    try:
        if adjustment_data.adjustment_type == "HOLIDAY":
            return _handle_holiday_adjustment(db, schedule, adjustment_data)
        elif adjustment_data.adjustment_type == "SWAP":
            return _handle_swap_adjustment(db, schedule, adjustment_data)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid adjustment type. Must be 'HOLIDAY' or 'SWAP'"
            )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process adjustment: {str(e)}"
        )


def _handle_holiday_adjustment(db: Session, schedule: Schedule, data: HolidayAdjustmentRequest) -> AdjustmentOperationResponse:
    """处理放假调整"""
    # 确定处理的日期范围
    start_date = data.holiday_date
    end_date = data.end_date if data.end_date else data.holiday_date
    
    # 验证日期范围
    if end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date cannot be earlier than start date"
        )
    
    total_affected = 0
    adjustment_ids = []
    
    # 为日期范围内的每一天创建调整记录
    current_date = start_date
    while current_date <= end_date:
        # 1. 记录调整操作
        adjustment = ScheduleAdjustment(
            schedule_id=schedule.id,
            adjustment_type="HOLIDAY",
            original_date=current_date,
            target_date=None
        )
        db.add(adjustment)
        db.flush()  # 获取 adjustment.id
        adjustment_ids.append(adjustment.id)
        
        # 2. 找出指定日期的所有活跃非覆盖事件
        target_events = db.query(Event).filter(
            Event.schedule_id == schedule.id,
            Event.is_active == True,
            Event.is_override == False,
            func.date(Event.start_time) == current_date
        ).all()
        
        # 3. 逻辑删除这些事件
        for event in target_events:
            event.is_active = False
            total_affected += 1
        
        # 移动到下一天
        current_date = current_date + timedelta(days=1)
    
    db.commit()
    
    # 生成消息
    if start_date == end_date:
        message = f"Successfully set {start_date} as holiday. {total_affected} events deactivated."
    else:
        days_count = (end_date - start_date).days + 1
        message = f"Successfully set {start_date} to {end_date} ({days_count} days) as holiday. {total_affected} events deactivated."
    
    return AdjustmentOperationResponse(
        success=True,
        message=message,
        adjustment_id=adjustment_ids[0] if adjustment_ids else None,
        affected_events=total_affected
    )


def _handle_swap_adjustment(db: Session, schedule: Schedule, data: SwapAdjustmentRequest) -> AdjustmentOperationResponse:
    """处理课程对调"""
    # 1. 记录调整操作
    adjustment = ScheduleAdjustment(
        schedule_id=schedule.id,
        adjustment_type="SWAP",
        original_date=data.source_date,
        target_date=data.target_date
    )
    db.add(adjustment)
    db.flush()  # 获取 adjustment.id
    
    # 2. 找出原始日期的所有活跃非覆盖事件
    from_events = db.query(Event).filter(
        Event.schedule_id == schedule.id,
        Event.is_active == True,
        Event.is_override == False,
        func.date(Event.start_time) == data.source_date
    ).all()
    
    # 3. 逻辑删除原始事件
    affected_count = 0
    for event in from_events:
        event.is_active = False
        affected_count += 1
    
    # 4. 为每个原始事件创建覆盖事件
    created_count = 0
    for original_event in from_events:
        # 计算新的时间
        original_start = original_event.start_time
        original_end = original_event.end_time
        
        # 保持时间部分，只改变日期部分
        new_start = datetime.combine(data.target_date, original_start.time())
        new_end = datetime.combine(data.target_date, original_end.time())
        
        # 创建覆盖事件
        override_event = Event(
            schedule_id=schedule.id,
            title=original_event.title,
            description=original_event.description,
            location=original_event.location,
            start_time=new_start,
            end_time=new_end,
            instructor=original_event.instructor,
            weeks_display=original_event.weeks_display,
            day_of_week=data.target_date.weekday() + 1,  # Python weekday: Monday=0, 我们的系统: Monday=1
            period=original_event.period,
            weeks_input=original_event.weeks_input,
            color=original_event.color,
            is_override=True,
            is_active=True,
            adjustment_id=adjustment.id
        )
        db.add(override_event)
        created_count += 1
    
    db.commit()
    
    return AdjustmentOperationResponse(
        success=True,
        message=f"Successfully swapped {affected_count} events from {data.source_date} to {data.target_date}. {created_count} override events created.",
        adjustment_id=adjustment.id,
        affected_events=affected_count
    )


@router.get("/{schedule_id}/adjustments", response_model=List[ScheduleAdjustmentResponse])
async def get_schedule_adjustments(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取课表的所有调休记录"""
    # 验证课表所有权
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.owner_id == current_user.id
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    adjustments = db.query(ScheduleAdjustment).filter(
        ScheduleAdjustment.schedule_id == schedule_id
    ).order_by(ScheduleAdjustment.created_at.desc()).all()
    
    return adjustments
