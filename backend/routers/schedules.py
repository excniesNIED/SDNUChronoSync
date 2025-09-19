from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime, timedelta
import ics

from database import get_db
from auth import get_current_user, get_current_admin_user
from models import User, Schedule, Event
from schemas import ScheduleCreate, ScheduleUpdate, ScheduleResponse, EventCreate, EventUpdate, EventResponse
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
    limit: int = 100
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
    
    events = db.query(Event).filter(
        Event.schedule_id == schedule_id
    ).offset(skip).limit(limit).all()
    
    return events


@router.post("/{schedule_id}/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule_event(
    schedule_id: int,
    event_data: EventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """在指定课表下创建事件"""
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
    
    # 创建事件
    db_event = Event(
        schedule_id=schedule_id,
        title=event_data.title,
        description=event_data.description,
        location=event_data.location,
        start_time=event_data.start_time,
        end_time=event_data.end_time,
        instructor=event_data.instructor,
        weeks_display=event_data.weeks_display,
        day_of_week=event_data.day_of_week,
        period=event_data.period,
        weeks_input=event_data.weeks_input
    )
    
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    return db_event


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
    
    # 获取所有事件
    events = db.query(Event).filter(Event.schedule_id == schedule_id).all()
    
    # 创建日历对象
    calendar = ics.Calendar()
    calendar.creator = f"Schedule Management System - {schedule.name}"
    
    # 遍历每个事件
    for event in events:
        # 解析周数
        weeks = parse_weeks(event.weeks_input or event.weeks_display or "")
        if not weeks:
            # 如果没有周数信息，创建单次事件
            weeks = [1]
        
        # 解析节次获取时间
        period_numbers = parse_period_to_class_numbers(event.period or "")
        
        # 获取开始和结束时间
        if period_numbers and schedule.class_times:
            first_period = str(period_numbers[0])
            last_period = str(period_numbers[-1])
            
            if first_period in schedule.class_times and last_period in schedule.class_times:
                start_time_str = schedule.class_times[first_period].get("start", "08:00")
                end_time_str = schedule.class_times[last_period].get("end", "09:00")
            else:
                # 使用事件原始时间
                start_time_str = event.start_time.strftime("%H:%M")
                end_time_str = event.end_time.strftime("%H:%M")
        else:
            # 使用事件原始时间
            start_time_str = event.start_time.strftime("%H:%M")
            end_time_str = event.end_time.strftime("%H:%M")
        
        # 为每个周数创建ICS事件
        for week_num in weeks:
            # 计算具体日期
            if event.day_of_week:
                # 基于星期几计算日期
                days_from_start = (week_num - 1) * 7 + (event.day_of_week - 1)
                event_date = schedule.start_date + timedelta(days=days_from_start)
            else:
                # 使用原始事件日期
                event_date = event.start_time.date()
            
            # 创建开始和结束时间
            start_hour, start_minute = map(int, start_time_str.split(':'))
            end_hour, end_minute = map(int, end_time_str.split(':'))
            
            start_datetime = datetime.combine(event_date, datetime.min.time().replace(
                hour=start_hour, minute=start_minute
            ))
            end_datetime = datetime.combine(event_date, datetime.min.time().replace(
                hour=end_hour, minute=end_minute
            ))
            
            # 创建ICS事件
            ics_event = ics.Event()
            ics_event.name = event.title
            ics_event.begin = start_datetime
            ics_event.end = end_datetime
            
            # 设置位置和描述
            location_parts = []
            if event.location:
                location_parts.append(event.location)
            if event.instructor:
                location_parts.append(event.instructor)
            
            if location_parts:
                ics_event.location = "|".join(location_parts)
                ics_event.description = "|".join(location_parts)
            
            # 添加提醒（提前10分钟）
            ics_event.alarms = [ics.DisplayAlarm(trigger=timedelta(minutes=-10))]
            
            # 生成唯一ID
            ics_event.uid = f"{schedule_id}{event.id}{week_num}{int(start_datetime.timestamp())}"
            
            calendar.events.add(ics_event)
    
    # 生成ICS内容
    ics_content = str(calendar)
    
    # 设置响应头
    filename = f"{schedule.name.replace(' ', '_')}.ics"
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"',
        'Content-Type': 'text/calendar; charset=utf-8'
    }
    
    return Response(content=ics_content, headers=headers)
