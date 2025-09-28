from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas import ImportSessionResponse, ImportRequest, ImportResponse, ScheduleResponse
from auth import get_current_user
from models import User, Event, Schedule
from importer import ZFWImporter
import crud

router = APIRouter(prefix="/api/import", tags=["import"])

@router.get("/schedules", response_model=List[ScheduleResponse])
async def get_user_schedules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的所有课表列表，用于导入时选择
    """
    schedules = db.query(Schedule).filter(Schedule.owner_id == current_user.id).all()
    return schedules

@router.get("/zfw/session", response_model=ImportSessionResponse)
async def get_import_session():
    """
    第一步：获取导入会话，包含验证码和CSRF token
    """
    try:
        session_data = ZFWImporter.create_session()
        return ImportSessionResponse(**session_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取导入会话失败: {str(e)}"
        )

@router.post("/zfw", response_model=ImportResponse)
async def import_from_zfw(
    import_request: ImportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    第二步：使用验证码和密码登录并导入课表
    """
    try:
        # 先确定使用的课表和开学日期
        target_schedule = None
        target_start_date = None
        
        if import_request.action == "use_existing" and import_request.schedule_id:
            # 使用现有课表
            target_schedule = db.query(Schedule).filter(
                Schedule.id == import_request.schedule_id,
                Schedule.owner_id == current_user.id
            ).first()
            
            if not target_schedule:
                return ImportResponse(
                    success=False,
                    message="指定的课表不存在或您没有权限访问"
                )
            
            target_start_date = target_schedule.start_date
        else:
            # 创建新课表时，使用用户指定的开学日期，如果没有则使用默认值
            target_start_date = import_request.start_date or date(2025, 9, 8)
        
        # 执行登录和导入，传入开学日期
        result = ZFWImporter.login_and_import(
            import_request.session_id,
            import_request.username,
            import_request.password,
            import_request.captcha,
            target_start_date
        )
        
        if not result["success"]:
            return ImportResponse(**result)
        
        # 获取导入的事件数据和用户信息
        events_data = result.get("events", [])
        user_info = result.get("user_info", None)
        
        if not events_data:
            return ImportResponse(
                success=False,
                message="未找到课表数据，请检查学号或联系管理员"
            )
        
        # 根据用户选择获取或创建课表
        if target_schedule:
            # 使用现有课表
            user_schedule = target_schedule
        else:
            # 创建新课表
            from datetime import date
            default_class_times = {
                "1": {"start": "08:20", "end": "09:05"},
                "2": {"start": "09:10", "end": "09:55"},
                "3": {"start": "10:10", "end": "10:55"},
                "4": {"start": "11:00", "end": "11:45"},
                "5": {"start": "14:00", "end": "14:45"},
                "6": {"start": "14:50", "end": "15:35"},
                "7": {"start": "15:50", "end": "16:35"},
                "8": {"start": "16:40", "end": "17:25"},
                "9": {"start": "19:00", "end": "19:45"},
                "10": {"start": "19:45", "end": "20:30"}
            }
            
            schedule_name = import_request.schedule_name or "导入的课表"
            user_schedule = Schedule(
                name=schedule_name,
                owner_id=current_user.id,
                status="进行",
                start_date=target_start_date,  # 使用确定的开学日期
                total_weeks=20,
                class_times=default_class_times
            )
            db.add(user_schedule)
            db.commit()  # 提交以获取schedule_id
            db.refresh(user_schedule)
        
        # 删除该课表下现有的课程类型事件，避免重复导入
        existing_courses = db.query(Event).filter(
            Event.schedule_id == user_schedule.id,
            Event.description.like("%教师:%")  # 简单的课程标识
        ).all()
        
        for course in existing_courses:
            db.delete(course)
        
        # 批量创建新事件
        imported_count = 0
        print(f"\n=== 开始创建数据库事件，共 {len(events_data)} 个事件 ===")
        for i, event_data in enumerate(events_data):
            try:
                print(f">>> 创建第 {i+1} 个数据库事件:")
                print(f"    标题: {event_data.get('title')}")
                print(f"    开始时间: {event_data.get('start_time')}")
                print(f"    结束时间: {event_data.get('end_time')}")
                print(f"    周数显示: {event_data.get('weeks_display')}")
                print(f"    星期几: {event_data.get('day_of_week')}")
                print(f"    节次: {event_data.get('period')}")
                
                db_event = Event(
                    schedule_id=user_schedule.id,
                    title=event_data.get('title'),
                    description=event_data.get('description'),
                    location=event_data.get('location'),
                    start_time=event_data.get('start_time'),
                    end_time=event_data.get('end_time'),
                    instructor=event_data.get('instructor'),
                    weeks_display=event_data.get('weeks_display'),
                    weeks_input=event_data.get('weeks_display'),  # 使用weeks_display作为weeks_input
                    day_of_week=event_data.get('day_of_week'),
                    period=event_data.get('period'),
                    color=event_data.get('color')  # 添加颜色字段
                )
                db.add(db_event)
                imported_count += 1
                print(f"    ✅ 成功添加到数据库")
            except Exception as e:
                print(f"    ❌ 创建事件失败: {e}")
                print(f"    事件数据: {event_data}")
                continue
        
        # 提交事务
        db.commit()
        
        # 打印最终结果
        print(f"\n=== 导入完成 ===")
        print(f"使用的课表ID: {user_schedule.id}")
        print(f"课表名称: {user_schedule.name}")
        print(f"课表拥有者: {current_user.id} ({current_user.full_name})")
        print(f"成功导入事件数: {imported_count}")
        
        # 验证数据库中的事件
        saved_events = db.query(Event).filter(Event.schedule_id == user_schedule.id).count()
        print(f"数据库中该课表的总事件数: {saved_events}")
        
        return ImportResponse(
            success=True,
            message=f"导入成功！共导入 {imported_count} 门课程",
            imported_count=imported_count,
            user_info=user_info
        )
        
    except Exception as e:
        db.rollback()
        error_message = str(e)
        
        return ImportResponse(
            success=False,
            message=f"导入失败：{error_message}"
        )

@router.get("/zfw/refresh/{session_id}", response_model=ImportSessionResponse)
async def refresh_captcha(session_id: str):
    """
    刷新验证码
    """
    try:
        # 从缓存中获取session
        from importer import _session_cache
        session_data = _session_cache.get(session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在或已过期"
            )
        
        session_obj = session_data.get("session")
        if session_obj == "fallback":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无法刷新验证码，请重新获取会话"
            )
        
        # 获取新的验证码
        import time
        timestamp = int(time.time() * 1000)
        captcha_url = f"http://jwxt.sdnu.edu.cn/jwglxt/kaptcha?time={timestamp}"
        
        captcha_response = session_obj.get(captcha_url, timeout=10)
        captcha_response.raise_for_status()
        
        # 检查响应类型
        content_type = captcha_response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="验证码获取失败"
            )
        
        # 转换为base64
        import base64
        captcha_base64 = base64.b64encode(captcha_response.content).decode('utf-8')
        
        return ImportSessionResponse(
            session_id=session_id,
            csrftoken=session_data.get("csrf_token", ""),
            captcha_image=captcha_base64
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刷新验证码失败: {str(e)}"
        )



