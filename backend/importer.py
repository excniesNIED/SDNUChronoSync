"""
山东师范大学正方教务系统课表导入器 - 支持两步验证
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import base64
import uuid
from typing import List, Dict, Optional
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import binascii
from schemas import EventCreate

# 会话缓存
_session_cache = {}

class ZFWImporter:
    """正方教务系统导入器 - 支持两步验证流程"""
    
    def __init__(self):
        self.base_url = "http://jwxt.sdnu.edu.cn"
        self.login_url = f"{self.base_url}/jwglxt/xtgl/login_slogin.html"
        self.captcha_url = f"{self.base_url}/jwglxt/xtgl/kaptcha"
        self.schedule_url = f"{self.base_url}/jwglxt/kbcx/xskbcx_cxXsKb.html"
        
        # RSA公钥参数 (需要从实际登录页面提取)
        self.rsa_modulus = "008aed7ad8c4f49fd1394d4c5c8a....."  # 这需要从实际页面获取
        self.rsa_exponent = "010001"  # 通常是这个值
    
    @classmethod
    def create_session(cls) -> Dict[str, str]:
        """第一步：创建登录会话，获取验证码和CSRF token"""
        try:
            session = requests.Session()
            session_id = str(uuid.uuid4())
            
            # 设置请求头
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            })
            
            importer = cls()
            
            # 1. 访问登录页面获取CSRF token
            login_page_response = session.get(importer.login_url)
            login_page_response.raise_for_status()
            
            soup = BeautifulSoup(login_page_response.text, 'lxml')
            csrf_token = ""
            
            # 提取CSRF token
            csrf_input = soup.find('input', {'id': 'csrftoken'}) or soup.find('input', {'name': 'csrftoken'})
            if csrf_input:
                csrf_token = csrf_input.get('value', '')
            
            # 2. 获取验证码图片
            captcha_response = session.get(importer.captcha_url)
            captcha_response.raise_for_status()
            
            # 将验证码图片转换为base64
            captcha_base64 = base64.b64encode(captcha_response.content).decode('utf-8')
            
            # 3. 缓存session对象
            _session_cache[session_id] = session
            
            return {
                "session_id": session_id,
                "csrftoken": csrf_token,
                "captcha_image": captcha_base64
            }
            
        except Exception as e:
            raise Exception(f"创建登录会话失败: {str(e)}")
    
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
    def login_and_import(cls, session_id: str, username: str, password: str, captcha: str) -> Dict:
        """第二步：使用验证码和密码登录并导入数据"""
        try:
            # 从缓存中获取session
            session = _session_cache.get(session_id)
            if not session:
                return {
                    "success": False,
                    "message": "会话已过期，请重新获取验证码",
                    "imported_count": 0
                }
            
            importer = cls()
            
            # 加密密码
            encrypted_password = importer.encrypt_password(password)
            
            # 准备登录数据
            login_data = {
                'yhm': username,
                'mm': encrypted_password,
                'yzm': captcha,
            }
            
            # 设置正确的请求头
            session.headers.update({
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': importer.login_url,
                'Origin': importer.base_url,
            })
            
            # 发送登录请求
            login_response = session.post(
                importer.login_url,
                data=login_data,
                allow_redirects=False
            )
            
            # 检查登录结果
            if login_response.status_code == 302:
                # 重定向通常表示登录成功
                redirect_location = login_response.headers.get('Location', '')
                if 'index' in redirect_location:
                    # 登录成功，开始获取课表
                    events = importer._fetch_and_parse_schedule(session)
                    
                    # 清理缓存
                    _session_cache.pop(session_id, None)
                    
                    return {
                        "success": True,
                        "message": f"导入成功！共导入 {len(events)} 门课程",
                        "imported_count": len(events),
                        "events": events
                    }
            
            # 登录失败
            _session_cache.pop(session_id, None)
            return {
                "success": False,
                "message": "登录失败，请检查用户名、密码或验证码是否正确",
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
    
    def _fetch_and_parse_schedule(self, session: requests.Session) -> List[Dict]:
        """获取并解析课表数据"""
        try:
            # 访问课表页面
            schedule_response = session.get(self.schedule_url)
            schedule_response.raise_for_status()
            
            # 解析课表HTML
            events = self.parse_schedule_html(schedule_response.text)
            
            return [event.dict() for event in events]
            
        except Exception as e:
            print(f"获取课表失败: {e}")
            return []
    
    def parse_schedule_html(self, html_content: str) -> List[EventCreate]:
        """解析课表HTML内容"""
        events = []
        
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            
            # 查找课表表格
            table = soup.find('table', {'id': 'Table1'}) or soup.find('table', class_='table')
            if not table:
                print("未找到课表表格")
                return events
            
            rows = table.find_all('tr')
            
            # 时间映射：第几节课对应的时间
            time_slots = {
                1: ("08:00", "08:45"),
                2: ("08:50", "09:35"),
                3: ("09:50", "10:35"),
                4: ("10:40", "11:25"),
                5: ("11:30", "12:15"),
                6: ("14:00", "14:45"),
                7: ("14:50", "15:35"),
                8: ("15:50", "16:35"),
                9: ("16:40", "17:25"),
                10: ("19:00", "19:45"),
                11: ("19:50", "20:35"),
                12: ("20:40", "21:25"),
            }
            
            # 解析每一行（跳过表头）
            for row_idx, row in enumerate(rows[1:], 1):
                cells = row.find_all(['td', 'th'])
                
                # 解析每一列（跳过第一列的时间标识）
                for col_idx, cell in enumerate(cells[1:], 1):
                    cell_text = cell.get_text(strip=True)
                    
                    if cell_text and cell_text != '':
                        # 解析课程信息
                        course_info = self._parse_course_cell(cell_text)
                        
                        if course_info:
                            # 计算星期几
                            day_of_week = col_idx
                            
                            # 计算节次
                            period_start = (row_idx - 1) * 2 + 1
                            period_end = period_start + 1
                            period_str = f"{period_start}-{period_end}节"
                            
                            # 获取时间
                            start_time_str, end_time_str = time_slots.get(period_start, ("08:00", "09:35"))
                            
                            # 生成事件
                            events.extend(self._create_events_from_course(
                                course_info, day_of_week, period_str,
                                start_time_str, end_time_str
                            ))
            
        except Exception as e:
            print(f"解析课表失败: {e}")
        
        return events
    
    def _parse_course_cell(self, cell_text: str) -> Optional[Dict]:
        """解析单元格中的课程信息"""
        try:
            # 课程信息通常格式为：课程名称<br>周数<br>教师<br>地点
            # 或者用换行符分隔
            lines = cell_text.replace('<br>', '\n').replace('<BR>', '\n').split('\n')
            lines = [line.strip() for line in lines if line.strip()]
            
            if len(lines) >= 1:
                return {
                    'title': lines[0],
                    'weeks_display': lines[1] if len(lines) > 1 else '',
                    'instructor': lines[2] if len(lines) > 2 else '',
                    'location': lines[3] if len(lines) > 3 else '',
                }
        except Exception as e:
            print(f"解析课程信息失败: {e}")
        
        return None
    
    def _create_events_from_course(self, course_info: Dict, day_of_week: int, 
                                 period: str, start_time_str: str, end_time_str: str) -> List[EventCreate]:
        """根据课程信息创建事件列表"""
        events = []
        
        # 解析周数信息
        weeks_text = course_info.get('weeks_display', '')
        week_numbers = self._parse_weeks(weeks_text)
        
        # 获取当前学期的开始日期（这里需要根据实际情况调整）
        semester_start = datetime(2024, 2, 26)  # 假设2024年春季学期开始日期
        
        # 为每个周数创建事件
        for week_num in week_numbers:
            # 计算具体日期
            target_date = semester_start + timedelta(weeks=week_num-1, days=day_of_week-1)
            
            # 创建开始和结束时间
            start_time = datetime.combine(target_date.date(), 
                                        datetime.strptime(start_time_str, "%H:%M").time())
            end_time = datetime.combine(target_date.date(), 
                                      datetime.strptime(end_time_str, "%H:%M").time())
            
            event = EventCreate(
                title=course_info['title'],
                description=f"教师: {course_info.get('instructor', '未知')}",
                location=course_info.get('location', ''),
                start_time=start_time,
                end_time=end_time,
                instructor=course_info.get('instructor', ''),
                weeks_display=weeks_text,
                day_of_week=day_of_week,
                period=period
            )
            
            events.append(event)
        
        return events
    
    def _parse_weeks(self, weeks_text: str) -> List[int]:
        """解析周数文本，返回周数列表"""
        week_numbers = []
        
        try:
            if not weeks_text:
                return list(range(1, 17))  # 默认1-16周
                
            # 处理常见的周数格式
            if '单周' in weeks_text:
                # 提取范围
                range_match = re.search(r'(\d+)-(\d+)周', weeks_text)
                if range_match:
                    start_week, end_week = int(range_match.group(1)), int(range_match.group(2))
                    week_numbers = [w for w in range(start_week, end_week + 1) if w % 2 == 1]
                    
            elif '双周' in weeks_text:
                range_match = re.search(r'(\d+)-(\d+)周', weeks_text)
                if range_match:
                    start_week, end_week = int(range_match.group(1)), int(range_match.group(2))
                    week_numbers = [w for w in range(start_week, end_week + 1) if w % 2 == 0]
                    
            elif '-' in weeks_text and '周' in weeks_text:
                # 连续周数，如 "1-16周"
                range_match = re.search(r'(\d+)-(\d+)', weeks_text)
                if range_match:
                    start_week, end_week = int(range_match.group(1)), int(range_match.group(2))
                    week_numbers = list(range(start_week, end_week + 1))
                    
            else:
                # 单独的周数或逗号分隔的周数
                numbers = re.findall(r'\d+', weeks_text)
                week_numbers = [int(n) for n in numbers if 1 <= int(n) <= 25]
                
        except Exception as e:
            print(f"解析周数失败: {e}")
            # 默认返回1-16周
            week_numbers = list(range(1, 17))
        
        return week_numbers if week_numbers else list(range(1, 17))