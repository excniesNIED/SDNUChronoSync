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
            - "4-18周" -> [4, 5, 6, ..., 18]
            - "第4-18周" -> [4, 5, 6, ..., 18]
            - "1,3,5" -> [1, 3, 5]
            - "1-5,8-10" -> [1, 2, 3, 4, 5, 8, 9, 10]
    
    Returns:
        List[int]: 解析后的周数列表
    """
    if not week_string or not week_string.strip():
        return []
    
    # 清理字符串：移除中文字符和替换各种破折号
    cleaned = week_string.strip()

    # 统一各类破折号、波浪号
    cleaned = (cleaned
               .replace('－', '-')
               .replace('—', '-')
               .replace('～', '-')
               .replace('〜', '-')
               .replace('~', '-'))

    # 去除中文括号及其中内容（例如“(单)”“（双）”）
    cleaned = re.sub(r'（.*?）', '', cleaned)
    cleaned = re.sub(r'\(.*?\)', '', cleaned)

    # 移除常见中文词汇（如“第”“周”“等”）
    cleaned = re.sub(r'[周第等上下单双（）()]', '', cleaned)

    # 移除空白字符
    cleaned = re.sub(r'\s+', '', cleaned)

    # 仅保留数字、逗号和连字符，其他全部去除
    cleaned = re.sub(r'[^0-9,\-]', '', cleaned)

    # 移除首尾逗号
    cleaned = cleaned.strip(',')
    
    if not cleaned:
        return []
    
    weeks = []
    
    # 按逗号分割
    parts = [p for p in cleaned.split(',') if p]
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        # 检查是否是范围（如 "4-18"）
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
        "1": {"start": "08:20", "end": "09:05"},   # 第一节课8.20-9.05
        "2": {"start": "09:10", "end": "09:55"},   # 第二节课9.10-9.55
        "3": {"start": "10:10", "end": "10:55"},   # 第三节课10.10-10.55
        "4": {"start": "11:00", "end": "11:45"},   # 第四节课11.00-11.45
        "5": {"start": "14:00", "end": "14:45"},   # 第五节课2.00-2.45
        "6": {"start": "14:50", "end": "15:35"},   # 第六节课2.50-3.35
        "7": {"start": "15:50", "end": "16:35"},   # 第七节课3.50-4.35
        "8": {"start": "16:40", "end": "17:25"},   # 第八节课4.40-5.25
        "9": {"start": "19:00", "end": "19:45"},   # 第九节课7.00-7.45
        "10": {"start": "19:45", "end": "20:30"},  # 第十节课7.45-8.30
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
