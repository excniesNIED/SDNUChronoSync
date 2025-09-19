from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import ImportSessionResponse, ImportRequest, ImportResponse
from auth import get_current_user
from models import User, Event
from importer import ZFWImporter
import crud

router = APIRouter(prefix="/api/import", tags=["import"])

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
        # 执行登录和导入
        result = ZFWImporter.login_and_import(
            import_request.session_id,
            import_request.username,
            import_request.password,
            import_request.captcha
        )
        
        if not result["success"]:
            return ImportResponse(**result)
        
        # 获取导入的事件数据
        events_data = result.get("events", [])
        
        if not events_data:
            return ImportResponse(
                success=False,
                message="未找到课表数据，请检查学号或联系管理员"
            )
        
        # 删除用户现有的课程类型事件，避免重复导入
        existing_courses = db.query(Event).filter(
            Event.owner_id == current_user.id,
            Event.description.like("%教师:%")  # 简单的课程标识
        ).all()
        
        for course in existing_courses:
            db.delete(course)
        
        # 批量创建新事件
        imported_count = 0
        for event_data in events_data:
            try:
                db_event = Event(
                    title=event_data.get('title'),
                    description=event_data.get('description'),
                    location=event_data.get('location'),
                    start_time=event_data.get('start_time'),
                    end_time=event_data.get('end_time'),
                    instructor=event_data.get('instructor'),
                    weeks_display=event_data.get('weeks_display'),
                    day_of_week=event_data.get('day_of_week'),
                    period=event_data.get('period'),
                    owner_id=current_user.id
                )
                db.add(db_event)
                imported_count += 1
            except Exception as e:
                print(f"创建事件失败: {e}")
                continue
        
        # 提交事务
        db.commit()
        
        return ImportResponse(
            success=True,
            message=f"导入成功！共导入 {imported_count} 门课程",
            imported_count=imported_count
        )
        
    except Exception as e:
        db.rollback()
        error_message = str(e)
        
        return ImportResponse(
            success=False,
            message=f"导入失败：{error_message}"
        )

@router.get("/test")
async def test_import_connection():
    """测试教务系统连接"""
    try:
        # 简单的连接测试
        import requests
        response = requests.get("http://jwxt.sdnu.edu.cn", timeout=5)
        
        if response.status_code == 200:
            return {"status": "success", "message": "教务系统连接正常"}
        else:
            return {"status": "error", "message": f"教务系统响应异常: {response.status_code}"}
            
    except Exception as e:
        return {"status": "error", "message": f"连接测试失败: {str(e)}"}