"""
山东师范大学正方教务系统课表导入器 - 基于新的登录流程
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import base64
import uuid
import time
import os
from typing import List, Dict, Optional
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import binascii
from PIL import Image
from schemas import EventCreate
import json

# 会话缓存
_session_cache = {}

class JwxtLogin:
    """山东师范大学教务系统登录器 - 基于新的登录流程"""
    
    def __init__(self, student_id, password):
        self.student_id = student_id
        self.password = password
        self.session = requests.Session()
        self.base_url = "http://jwxt.sdnu.edu.cn/jwglxt"
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0'
        })

    def _get_csrf_token(self):
        """获取CSRF token"""
        print("[1] 正在访问登录页面以获取csrftoken...")
        try:
            login_page_url = f"{self.base_url}/xtgl/login_slogin.html"
            resp = self.session.get(login_page_url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            token_element = soup.find('input', {'id': 'csrftoken'})
            if token_element: 
                return token_element.get('value')
            return None
        except Exception: 
            return None

    def _get_encrypted_password(self):
        """获取RSA加密的密码"""
        print("[2] 正在获取RSA公钥...")
        try:
            key_url = f"{self.base_url}/xtgl/login_getPublicKey.html"
            resp = self.session.get(key_url)
            resp.raise_for_status()
            key_data = resp.json()
            modulus_bytes = base64.b64decode(key_data['modulus'])
            exponent_bytes = base64.b64decode(key_data['exponent'])
            modulus = int.from_bytes(modulus_bytes, 'big')
            exponent = int.from_bytes(exponent_bytes, 'big')
            
            print("[3] 正在使用公钥加密密码...")
            rsa_key = RSA.construct((modulus, exponent))
            cipher = PKCS1_v1_5.new(rsa_key)
            encrypted_bytes = cipher.encrypt(self.password.encode('utf-8'))
            encrypted_password = base64.b64encode(encrypted_bytes).decode('utf-8')
            print("    -> 密码加密完成。")
            return encrypted_password
        except Exception as e:
            print(f"    -> [错误] 加密密码时出错: {e}")
            return None

    def _get_captcha_code(self):
        """获取验证码并返回base64编码"""
        print("[4] 正在获取验证码...")
        try:
            timestamp = int(time.time() * 1000)
            captcha_url = f"{self.base_url}/kaptcha?time={timestamp}"
            resp = self.session.get(captcha_url)
            resp.raise_for_status()
            
            # 返回验证码的base64编码供前端显示
            captcha_base64 = base64.b64encode(resp.content).decode('utf-8')
            return captcha_base64
        except Exception as e:
            print(f"    -> [错误] 获取验证码失败: {e}")
            return None

    def login_with_captcha(self, captcha_code):
        """使用验证码登录"""
        print("[5] 正在提交登录请求...")
        
        # 获取必要的登录信息
        csrftoken = self._get_csrf_token()
        if not csrftoken: 
            print("[错误] 步骤1失败: 无法获取csrftoken。")
            return False

        encrypted_password = self._get_encrypted_password()
        if not encrypted_password: 
            return False
        
        login_post_url = f"{self.base_url}/xtgl/login_slogin.html"
        payload = {
            'csrftoken': csrftoken, 
            'yhm': self.student_id, 
            'mm': encrypted_password,
            'yzm': captcha_code, 
            'language': 'zh_CN', 
            'ydType': 'yhm'
        }
        
        try:
            resp_login = self.session.post(login_post_url, data=payload)
            resp_login.raise_for_status()
            
            # 检查登录是否成功（通过重定向判断）
            if resp_login.history:
                print("[6] ✅ POST请求成功，服务器已重定向！正在进入主系统...")
                
                # 模拟点击"已阅读"后的跳转，进入主界面
                index_url = f"{self.base_url}/xtgl/login_loginIndex.html"
                self.session.get(index_url)
                print("[7] ✅ 成功进入主系统！登录流程全部完成。")
                return True
            else:
                # 检查具体的错误信息
                if "用户名或密码不正确" in resp_login.text:
                     print("[6] ❌ 登录失败: 用户名或密码不正确！")
                elif "验证码输入错误" in resp_login.text:
                     print("[6] ❌ 登录失败: 验证码输入错误！")
                else:
                    print("[6] ❌ 登录失败: 验证码很可能输入错误。")
                return False

        except requests.exceptions.RequestException as e:
            print(f"    -> [错误] 提交登录请求时失败: {e}")
            return False

    def get_schedule(self, year, term):
        """获取课表数据"""
        print("\n[*] 正在尝试获取课表...")
        schedule_url = f"{self.base_url}/kbcx/xskbcx_cxXsgrkb.html?gnmkdm=N253508"
        term_code = '3' if term == 1 else '12'
        schedule_payload = {'xnm': str(year), 'xqm': term_code}
        try:
            resp = self.session.post(schedule_url, data=schedule_payload)
            resp.raise_for_status()
            print("[+] 成功获取课表数据！")
            return resp.json()
        except Exception as e:
            print(f"[-] 获取课表失败: {e}")
            return None


class ZFWImporter:
    """正方教务系统导入器 - 基于新的登录流程"""
    
    # 教务系统相关URL
    login_url = "http://jwxt.sdnu.edu.cn/jwglxt/xtgl/login_slogin.html"
    schedule_urls = [
        "http://jwxt.sdnu.edu.cn/jwglxt/kbcx/xskbcx_cxXsgrkb.html?gnmkdm=N253508"
    ]
    
    @classmethod
    def create_session(cls) -> Dict[str, str]:
        """第一步：创建登录会话，获取验证码"""
        session_id = str(uuid.uuid4())
        
        try:
            # 创建临时的登录器来获取验证码
            temp_login = JwxtLogin("temp", "temp")
            
            # 获取验证码图片
            captcha_base64 = temp_login._get_captcha_code()
            if not captcha_base64:
                raise Exception("获取验证码失败")
            
            # 缓存session信息
            _session_cache[session_id] = {
                "login_session": temp_login.session,
                "created_time": datetime.now().timestamp(),
            }
            
            return {
                "session_id": session_id,
                "csrftoken": "dummy_token",  # 保持兼容性
                "captcha_image": captcha_base64,
                "source": "real"
            }
            
        except Exception as e:
            print(f"创建会话失败: {e}")
            raise Exception(f"创建登录会话失败: {str(e)}")
    
    @classmethod
    def _create_fallback_session(cls, session_id: str) -> Dict[str, str]:
        """创建fallback session（当无法访问真实教务系统时）"""
        print("使用fallback验证码...")
        
        try:
            # 生成一个包含文本的验证码图片
            from PIL import Image, ImageDraw, ImageFont
            import io
            import random
            import string
            
            # 生成随机验证码文本
            captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            
            # 创建一个验证码图片 (108x34 匹配真实验证码尺寸)
            img = Image.new('RGB', (108, 34), color=(255, 255, 255))
            draw = ImageDraw.Draw(img)
            
            try:
                # 尝试使用系统字体
                font = ImageFont.truetype("arial.ttf", 18)
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
                except:
                    # 如果没有找到字体，使用默认字体
                    font = ImageFont.load_default()
            
            # 添加背景干扰线
            for _ in range(3):
                x1, y1 = random.randint(0, 108), random.randint(0, 34)
                x2, y2 = random.randint(0, 108), random.randint(0, 34)
                draw.line([(x1, y1), (x2, y2)], fill=(200, 200, 200), width=1)
            
            # 绘制验证码文本
            text_width = draw.textlength(captcha_text, font=font) if hasattr(draw, 'textlength') else len(captcha_text) * 12
            x = (108 - text_width) // 2
            y = 8
            draw.text((x, y), captcha_text, fill=(0, 0, 0), font=font)
            
            # 添加噪点
            for _ in range(50):
                x, y = random.randint(0, 107), random.randint(0, 33)
                draw.point((x, y), fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
            
            # 转换为base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            captcha_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
        except ImportError:
            # 如果PIL不可用，使用固定验证码
            captcha_text = "DEMO"
            # 使用一个简单的PNG图片数据
            captcha_base64 = base64.b64encode(
                b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00l\x00\x00\x00"\x08\x02\x00\x00\x00\x9b\xc5\x07\x02\x00\x00\x00\x19tEXtSoftware\x00Adobe ImageReadyq\xc9e<\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00IEND\xaeB`\x82'
            ).decode('utf-8')
        except Exception as e:
            print(f"生成fallback验证码失败: {e}")
            captcha_text = "1234"
            captcha_base64 = ""
        
        # 缓存fallback session信息
        _session_cache[session_id] = {
            "session": "fallback",
            "captcha_answer": captcha_text,
            "created_time": datetime.now().timestamp(),
            "csrf_token": f"fallback_csrf_{session_id[:8]}"
        }
        
        return {
            "session_id": session_id,
            "csrftoken": f"fallback_csrf_{session_id[:8]}",
            "captcha_image": captcha_base64,
            "source": "fallback"  # 标识这是fallback验证码
        }
    
    def encrypt_password(self, password: str) -> str:
        """使用RSA加密密码"""
        try:
            # 这里需要实现RSA加密
            # 由于实际的RSA参数需要从登录页面动态获取，这里先返回原密码
            # 在实际部署时需要分析登录页面的JavaScript来获取正确的RSA参数
            return password  # 临时实现
            
        except Exception as e:
            print(f"密码加密失败: {e}")
            return password
    
    @classmethod 
    def _parse_schedule_json(cls, schedule_data: Dict) -> List[Dict]:
        """解析从教务系统获取的JSON格式课表数据"""
        events = []
        
        try:
            # 获取课表列表
            kb_list = schedule_data.get('kbList', [])
            print(f"解析课表数据，共 {len(kb_list)} 门课程")
            
            # 解析每门课程
            for i, course in enumerate(kb_list):
                try:
                    print(f"\n>>> 解析第 {i+1} 门课程:")
                    print(f"    原始课程数据: {course}")
                    
                    # 提取课程基本信息
                    course_name = course.get('kcmc', '未知课程')  # 课程名称
                    teacher_name = course.get('xm', '未知教师')   # 教师姓名
                    classroom = course.get('cdmc', '未知教室')     # 教室名称
                    
                    print(f"    课程名称: {course_name}")
                    print(f"    教师: {teacher_name}")
                    print(f"    教室: {classroom}")
                    
                    # 时间信息
                    week_day = int(course.get('xqj', 1))  # 星期几 (1-7)
                    print(f"    星期: {week_day}")
                    
                    # 解析节次信息，格式如 "3-4"
                    jcor_str = course.get('jcor', '1')
                    print(f"    原始节次(jcor): {jcor_str}")
                    if '-' in jcor_str:
                        periods = jcor_str.split('-')
                        start_period = int(periods[0])
                        end_period = int(periods[1])
                    else:
                        start_period = int(jcor_str)
                        end_period = start_period
                    
                    print(f"    解析后节次: {start_period}-{end_period}")
                    
                    # 周数信息
                    weeks_display = course.get('zcd', '1-16周')  # 周次显示
                    print(f"    原始周次显示(zcd): {weeks_display}")
                    
                    # 解析具体的周数
                    week_numbers = cls._parse_weeks_from_zcd(weeks_display)
                    print(f"    解析后周数: {week_numbers}")
                    
                    # 获取上课时间
                    start_time_str, end_time_str = cls._get_period_time(start_period, end_period)
                    print(f"    计算出的时间: {start_time_str} - {end_time_str}")
                    
                    # 2025年第一学期开始日期（第一周为9月7日）
                    semester_start = datetime(2025, 9, 7)  # 第一周从9月7日开始
                    
                    # 为每个周数创建事件
                    for week_num in week_numbers:
                        try:
                            # 计算具体日期 
                            # week_num-1: 因为第1周是起始周
                            # week_day-1: 因为星期一是1，但我们需要0-6的偏移
                            days_offset = (week_num - 1) * 7 + (week_day - 1)
                            target_date = semester_start + timedelta(days=days_offset)
                            print(f"        第{week_num}周 星期{week_day}: {semester_start} + {days_offset}天 = {target_date}")
                            
                            # 创建开始和结束时间
                            start_time = datetime.combine(target_date.date(), 
                                                        datetime.strptime(start_time_str, "%H:%M").time())
                            end_time = datetime.combine(target_date.date(), 
                                                      datetime.strptime(end_time_str, "%H:%M").time())
                            
                            # 为课程分配颜色
                            course_color = cls._get_course_color(course_name)
                            
                            event = {
                                "title": course_name,
                                "description": f"教师: {teacher_name}",
                                "location": classroom,
                                "start_time": start_time,
                                "end_time": end_time,
                                "instructor": teacher_name,
                                "weeks_display": weeks_display,
                                "day_of_week": week_day,
                                "period": f"{start_period}-{end_period}节",
                                "color": course_color
                            }
                            
                            events.append(event)
                            
                        except Exception as e:
                            print(f"创建课程事件失败 (第{week_num}周): {e}")
                            continue
                    
                    print(f"课程 '{course_name}' 生成了 {len(week_numbers)} 个事件")
                    
                except Exception as e:
                    print(f"解析课程失败: {e}, 课程数据: {course}")
                    continue
            
            print(f"总共生成 {len(events)} 个课表事件")
            return events
            
        except Exception as e:
            print(f"解析课表JSON数据失败: {e}")
            return []
    
    @classmethod
    def _parse_weeks_from_zcd(cls, zcd: str) -> List[int]:
        """解析周次显示字符串(zcd)，返回周数列表"""
        week_numbers = []
        
        try:
            if not zcd:
                return list(range(1, 17))
            
            # 示例格式: "1-16周" "1-8周(单)" "2-16周(双)"
            import re
            
            # 处理单双周
            is_odd = '(单)' in zcd
            is_even = '(双)' in zcd
            
            # 提取周数范围
            range_match = re.search(r'(\d+)-(\d+)周', zcd)
            if range_match:
                start_week = int(range_match.group(1))
                end_week = int(range_match.group(2))
                
                if is_odd:
                    # 单周
                    week_numbers = [w for w in range(start_week, end_week + 1) if w % 2 == 1]
                elif is_even:
                    # 双周
                    week_numbers = [w for w in range(start_week, end_week + 1) if w % 2 == 0]
                else:
                    # 所有周
                    week_numbers = list(range(start_week, end_week + 1))
            else:
                # 如果没有匹配到范围，默认1-16周
                week_numbers = list(range(1, 17))
            
            return week_numbers if week_numbers else list(range(1, 17))
            
        except Exception as e:
            print(f"解析周次失败: {e}")
            return list(range(1, 17))
    
    @classmethod
    def _get_period_time(cls, start_period: int, end_period: int) -> tuple:
        """根据节次获取上课时间"""
        # 山东师范大学作息时间表（根据用户提供的正确时间）
        time_table = {
            1: ("08:20", "09:05"),  # 第一节课8.20-9.05
            2: ("09:10", "09:55"),  # 第二节课9.10-9.55
            3: ("10:10", "10:55"),  # 第三节课10.10-10.55
            4: ("11:00", "11:45"),  # 第四节课11.00-11.45
            5: ("14:00", "14:45"),  # 第五节课2.00-2.45
            6: ("14:50", "15:35"),  # 第六节课2.50-3.35
            7: ("15:50", "16:35"),  # 第七节课3.50-4.35
            8: ("16:40", "17:25"),  # 第八节课4.40-5.25
            9: ("19:00", "19:45"),  # 第九节课7.00-7.45
            10: ("19:45", "20:30"), # 第十节课7.45-8.30
        }
        
        try:
            start_time = time_table.get(start_period, ("08:20", "09:05"))[0]
            end_time = time_table.get(end_period, ("09:05", "09:05"))[1]
            print(f"    节次 {start_period}-{end_period} 对应时间: {start_time}-{end_time}")
            return start_time, end_time
        except Exception as e:
            print(f"获取节次时间失败: {e}")
            return "08:20", "09:05"

    @classmethod
    def _get_course_color(cls, course_name: str) -> str:
        """根据课程名称分配颜色"""
        # 预定义的颜色调色板
        colors = [
            "#3B82F6",  # 蓝色
            "#10B981",  # 绿色
            "#F59E0B",  # 黄色
            "#EF4444",  # 红色
            "#8B5CF6",  # 紫色
            "#06B6D4",  # 青色
            "#84CC16",  # 柠檬绿
            "#F97316",  # 橙色
            "#EC4899",  # 粉色
            "#6B7280",  # 灰色
            "#14B8A6",  # 青绿色
            "#DC2626",  # 深红色
            "#7C3AED",  # 深紫色
            "#059669",  # 深绿色
            "#D97706",  # 深橙色
        ]
        
        # 使用课程名称的哈希值来确定颜色，确保同一课程总是使用同一颜色
        import hashlib
        hash_object = hashlib.md5(course_name.encode())
        hash_int = int(hash_object.hexdigest(), 16)
        color_index = hash_int % len(colors)
        
        return colors[color_index]

    @classmethod
    def login_and_import(cls, session_id: str, username: str, password: str, captcha: str) -> Dict:
        """第二步：使用验证码和密码登录并导入数据"""
        try:
            # 从缓存中获取session
            session_data = _session_cache.get(session_id)
            if not session_data:
                return {
                    "success": False,
                    "message": "会话已过期，请重新获取验证码",
                    "imported_count": 0
                }
            
            # 检查session是否过期（30分钟）
            current_time = datetime.now().timestamp()
            if current_time - session_data.get("created_time", 0) > 1800:  # 30分钟
                _session_cache.pop(session_id, None)
                return {
                    "success": False,
                    "message": "会话已过期，请重新获取验证码",
                    "imported_count": 0
                }
            
            # 输入验证
            if not username or not password or not captcha:
                return {
                    "success": False,
                    "message": "请填写完整的登录信息",
                    "imported_count": 0
                }
            
            try:
                print(f"开始登录流程，用户名: {username}")
                
                # 创建新的登录器实例
                jwxt_login = JwxtLogin(username, password)
                
                # 使用缓存的session（保持cookies）
                if "login_session" in session_data:
                    jwxt_login.session = session_data["login_session"]
                
                # 尝试登录
                login_success = jwxt_login.login_with_captcha(captcha)
                
                if not login_success:
                    # 清理缓存
                    _session_cache.pop(session_id, None)
                    return {
                        "success": False,
                        "message": "登录失败，请检查学号、密码或验证码是否正确",
                        "imported_count": 0
                    }
                
                # 登录成功，获取课表数据
                print("登录成功，开始获取课表数据...")
                schedule_data = jwxt_login.get_schedule(year=2025, term=1)
                
                if not schedule_data:
                    # 清理缓存
                    _session_cache.pop(session_id, None)
                    return {
                        "success": False,
                        "message": "获取课表数据失败，请稍后重试",
                        "imported_count": 0
                    }
                
                # 打印原始JSON数据用于调试
                print("=" * 50)
                print("获取到的原始课表JSON数据:")
                import json
                print(json.dumps(schedule_data, indent=2, ensure_ascii=False))
                print("=" * 50)
                
                # 解析课表数据
                events = cls._parse_schedule_json(schedule_data)
                
                # 清理缓存
                _session_cache.pop(session_id, None)
                
                return {
                    "success": True,
                    "message": f"课表导入成功！共获取到 {len(events)} 个事件",
                    "imported_count": len(events),
                    "events": events
                }
                
            except Exception as e:
                print(f"登录或获取课表异常: {e}")
                # 清理缓存
                _session_cache.pop(session_id, None)
                return {
                    "success": False,
                    "message": f"登录过程中发生错误: {str(e)}",
                    "imported_count": 0
                }
            
        except Exception as e:
            # 清理缓存
            _session_cache.pop(session_id, None)
            return {
                "success": False,
                "message": f"导入过程中发生错误: {str(e)}",
                "imported_count": 0
            }