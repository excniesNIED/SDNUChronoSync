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
        
        # 根据用户选择获取或创建课表
        user_schedule = None
        
        if import_request.action == "use_existing" and import_request.schedule_id:
            # 使用现有课表
            user_schedule = db.query(Schedule).filter(
                Schedule.id == import_request.schedule_id,
                Schedule.owner_id == current_user.id
            ).first()
            
            if not user_schedule:
                return ImportResponse(
                    success=False,
                    message="指定的课表不存在或您没有权限访问",
                    imported_count=0
                )
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
                start_date=date(2025, 9, 7),  # 2025年第一学期开始日期（第一周）
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
            imported_count=imported_count
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

@router.post("/test-login")
async def test_login_flow(
    import_request: ImportRequest
):
    """测试登录流程 - 只验证登录是否成功，不导入数据"""
    try:
        # 从缓存中获取session
        from importer import _session_cache
        session_data = _session_cache.get(import_request.session_id)
        if not session_data:
            return {
                "success": False,
                "message": "会话已过期，请重新获取验证码",
                "details": []
            }
        
        # 获取session对象和相关信息
        session_obj = session_data.get("session")
        csrf_token = session_data.get("csrf_token", "")
        
        if session_obj == "fallback":
            return {
                "success": False,
                "message": "这是fallback会话，无法测试真实登录",
                "details": []
            }
        
        # 执行登录测试
        result = await test_real_login(
            session_obj, 
            import_request.username, 
            import_request.password, 
            import_request.captcha, 
            csrf_token
        )
        
        # 清理缓存
        _session_cache.pop(import_request.session_id, None)
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"测试过程中发生错误: {str(e)}",
            "details": []
        }

async def test_real_login(session, username: str, password: str, captcha: str, csrf_token: str):
    """测试真实登录流程"""
    details = []
    
    try:
        from importer import ZFWImporter
        importer = ZFWImporter()
        
        details.append("=== 开始登录测试 ===")
        details.append(f"用户名: {username}")
        details.append(f"验证码: {captcha}")
        details.append(f"CSRF Token: {csrf_token[:20]}..." if csrf_token else "无CSRF Token")
        
        # 构建登录数据
        login_data = {
            'yhm': username,  # 用户名
            'mm': password,   # 密码
            'yzm': captcha,   # 验证码
        }
        
        # 如果有CSRF token，添加到数据中
        if csrf_token:
            login_data.update({
                'csrftoken': csrf_token,
                '_token': csrf_token,
                '__VIEWSTATE': csrf_token
            })
        
        details.append(f"登录URL: {importer.login_url}")
        details.append("正在发送登录请求...")
        
        # 发送登录请求
        login_response = session.post(
            importer.login_url,
            data=login_data,
            timeout=15,
            allow_redirects=False  # 不自动跟随重定向
        )
        
        details.append(f"登录响应状态码: {login_response.status_code}")
        details.append(f"响应头: {dict(login_response.headers)}")
        
        # 检查登录结果
        if login_response.status_code == 302:
            # 重定向通常表示登录成功
            location = login_response.headers.get('Location', '')
            details.append(f"重定向到: {location}")
            
            if 'index' in location.lower() or 'main' in location.lower() or 'home' in location.lower():
                details.append("✅ 登录成功！检测到成功重定向")
                
                # 测试访问课表页面
                return await test_schedule_access(session, details)
                
            elif 'login' in location.lower():
                details.append("❌ 登录失败：重定向回登录页面")
                return {
                    "success": False,
                    "message": "登录失败，用户名、密码或验证码错误",
                    "details": details
                }
            else:
                details.append("⚠️ 未知重定向，尝试访问课表页面")
                return await test_schedule_access(session, details)
                
        elif login_response.status_code == 200:
            # 检查响应内容
            response_text = login_response.text
            details.append(f"登录响应内容长度: {len(response_text)}")
            
            # 检查是否包含错误信息
            error_keywords = ['验证码错误', '用户名或密码错误', '登录失败', '账号或密码错误', '验证码不正确']
            for error_keyword in error_keywords:
                if error_keyword in response_text:
                    details.append(f"❌ 登录失败：检测到错误信息 '{error_keyword}'")
                    if '验证码' in error_keyword:
                        return {
                            "success": False,
                            "message": "验证码错误，请重新输入",
                            "details": details
                        }
                    else:
                        return {
                            "success": False,
                            "message": "用户名或密码错误",
                            "details": details
                        }
            
            # 检查是否包含成功标识
            success_keywords = ['欢迎', '课表', '学生信息', '个人中心', '教学管理']
            if any(keyword in response_text for keyword in success_keywords):
                details.append("✅ 登录成功！检测到成功标识")
                return await test_schedule_access(session, details)
            else:
                details.append("⚠️ 未检测到明确的成功/失败标识，尝试访问课表页面")
                return await test_schedule_access(session, details)
        else:
            details.append(f"❌ 登录请求失败，状态码: {login_response.status_code}")
            return {
                "success": False,
                "message": f"登录请求失败，状态码: {login_response.status_code}",
                "details": details
            }
            
    except Exception as e:
        details.append(f"❌ 登录过程异常: {str(e)}")
        return {
            "success": False,
            "message": f"登录过程中发生错误: {str(e)}",
            "details": details
        }

async def test_schedule_access(session, details):
    """测试课表页面访问"""
    try:
        from importer import ZFWImporter
        importer = ZFWImporter()
        
        details.append("\n=== 开始测试课表页面访问 ===")
        
        # 测试所有课表URL
        for i, schedule_url in enumerate(importer.schedule_urls):
            try:
                details.append(f"测试URL {i+1}: {schedule_url}")
                
                # 获取课表页面
                schedule_response = session.get(schedule_url, timeout=15)
                details.append(f"响应状态码: {schedule_response.status_code}")
                details.append(f"响应内容长度: {len(schedule_response.text)}")
                details.append(f"内容类型: {schedule_response.headers.get('content-type', '未知')}")
                
                # 检查页面内容
                if schedule_response.status_code == 200:
                    if len(schedule_response.text) > 1000:
                        # 检查是否包含课表相关内容
                        if '课表' in schedule_response.text or 'timetable' in schedule_response.text or 'td_wrap' in schedule_response.text:
                            details.append(f"✅ URL {i+1} 访问成功！包含课表内容")
                            details.append(f"页面前200字符: {schedule_response.text[:200]}")
                            
                            return {
                                "success": True,
                                "message": "登录成功，课表页面访问正常",
                                "details": details,
                                "working_url": schedule_url
                            }
                        else:
                            details.append(f"⚠️ URL {i+1} 访问成功但不包含课表内容")
                            details.append(f"页面前200字符: {schedule_response.text[:200]}")
                    else:
                        details.append(f"⚠️ URL {i+1} 页面内容过短")
                else:
                    details.append(f"❌ URL {i+1} 响应状态码异常: {schedule_response.status_code}")
                    
            except Exception as e:
                details.append(f"❌ URL {i+1} 访问异常: {str(e)}")
                continue
        
        # 如果所有URL都无法正常访问
        details.append("❌ 所有课表URL都无法正常访问")
        return {
            "success": False,
            "message": "登录成功，但无法访问课表页面",
            "details": details
        }
        
    except Exception as e:
        details.append(f"❌ 课表页面测试异常: {str(e)}")
        return {
            "success": False,
            "message": f"课表页面测试失败: {str(e)}",
            "details": details
        }

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