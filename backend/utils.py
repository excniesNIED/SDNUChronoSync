"""
Utility functions for the schedule management system
"""

import re
from typing import List


def parse_weeks(week_string: str) -> List[int]:
    """
    解析周数字符串，将 '1,4-6,9' 这样的字符串解析成整数列表 [1, 4, 5, 6, 9]
    
    Args:
        week_string: 周数字符串，支持格式如：
            - "1,4-6,9" -> [1, 4, 5, 6, 9]
            - "1-16" -> [1, 2, 3, ..., 16]
            - "1,3,5" -> [1, 3, 5]
            - "1-5,8-10" -> [1, 2, 3, 4, 5, 8, 9, 10]
    
    Returns:
        List[int]: 解析后的周数列表
    """
    if not week_string or not week_string.strip():
        return []
    
    weeks = []
    
    # 按逗号分割
    parts = week_string.strip().split(',')
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        # 检查是否是范围（如 "4-6"）
        if '-' in part:
            try:
                start, end = part.split('-', 1)
                start_week = int(start.strip())
                end_week = int(end.strip())
                
                # 确保范围有效
                if start_week <= end_week and 1 <= start_week <= 30 and 1 <= end_week <= 30:
                    weeks.extend(range(start_week, end_week + 1))
            except ValueError:
                # 忽略无效的范围
                continue
        else:
            # 单个周数
            try:
                week_num = int(part.strip())
                if 1 <= week_num <= 30:
                    weeks.append(week_num)
            except ValueError:
                # 忽略无效的周数
                continue
    
    # 去重并排序
    return sorted(list(set(weeks)))


def get_default_class_times() -> dict:
    """
    获取默认的上课时间配置
    
    Returns:
        dict: 默认的上课时间，键为节次，值为包含开始和结束时间的字典
    """
    return {
        "1": {"start": "08:00", "end": "08:45"},
        "2": {"start": "08:50", "end": "09:35"},
        "3": {"start": "09:50", "end": "10:35"},
        "4": {"start": "10:40", "end": "11:25"},
        "5": {"start": "11:30", "end": "12:15"},
        "6": {"start": "14:00", "end": "14:45"},
        "7": {"start": "14:50", "end": "15:35"},
        "8": {"start": "15:50", "end": "16:35"},
        "9": {"start": "16:40", "end": "17:25"},
        "10": {"start": "19:00", "end": "19:45"},
        "11": {"start": "19:50", "end": "20:35"},
    }


def parse_period_to_class_numbers(period_str: str) -> List[int]:
    """
    解析节次字符串，将 "1-2节" 转换为 [1, 2]
    
    Args:
        period_str: 节次字符串，如 "1-2节", "3节", "5-6节"
    
    Returns:
        List[int]: 节次数字列表
    """
    if not period_str:
        return []
    
    # 移除"节"字
    period_str = period_str.replace('节', '').strip()
    
    if '-' in period_str:
        try:
            start, end = period_str.split('-', 1)
            start_num = int(start.strip())
            end_num = int(end.strip())
            return list(range(start_num, end_num + 1))
        except ValueError:
            return []
    else:
        try:
            return [int(period_str.strip())]
        except ValueError:
            return []
