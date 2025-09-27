#!/usr/bin/env python3
"""
测试周数解析函数的脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import parse_weeks

def test_weeks_parsing():
    """测试周数解析功能"""
    print("🔍 测试周数解析功能")
    print("=" * 50)
    
    # 测试用例
    test_cases = [
        "4-18周",      # 您遇到的问题
        "1-16周",      # 常见格式
        "1,4-6,9",     # 混合格式
        "1-5,8-10",    # 多个范围
        "1,3,5",       # 单独数字
        "4-18",        # 不带"周"字
        "1-16",        # 不带"周"字
        "第4-18周",    # 带"第"字
        "4~18周",      # 用波浪号
        "4－18周",     # 中文破折号
    ]
    
    for test_case in test_cases:
        print(f"\n测试: '{test_case}'")
        
        # 显示原始字符串的详细信息
        print(f"  原始字符串长度: {len(test_case)}")
        print(f"  原始字符串字符: {[c for c in test_case]}")
        print(f"  原始字符串Unicode: {[ord(c) for c in test_case]}")
        
        # 测试解析
        result = parse_weeks(test_case)
        print(f"  解析结果: {result}")
        
        # 分步骤调试解析过程
        debug_parse_weeks(test_case)

def debug_parse_weeks(week_string: str):
    """调试周数解析过程"""
    print(f"  === 调试解析过程 ===")
    
    if not week_string or not week_string.strip():
        print(f"    空字符串，返回 []")
        return
    
    # 清理字符串
    cleaned = week_string.strip()
    print(f"    清理后: '{cleaned}'")
    
    # 移除"周"、"第"等字符
    import re
    # 尝试移除常见的中文字符
    cleaned = re.sub(r'[周第]', '', cleaned)
    print(f"    移除中文后: '{cleaned}'")
    
    # 替换中文破折号和波浪号
    cleaned = cleaned.replace('－', '-').replace('～', '-').replace('~', '-')
    print(f"    替换符号后: '{cleaned}'")
    
    weeks = []
    
    # 按逗号分割
    parts = cleaned.split(',')
    print(f"    分割后的部分: {parts}")
    
    for i, part in enumerate(parts):
        part = part.strip()
        print(f"    处理第 {i+1} 部分: '{part}'")
        
        if not part:
            print(f"      空部分，跳过")
            continue
            
        # 检查是否是范围（如 "4-18"）
        if '-' in part:
            print(f"      发现范围格式")
            try:
                start, end = part.split('-', 1)
                start_week = int(start.strip())
                end_week = int(end.strip())
                print(f"      范围: {start_week} 到 {end_week}")
                
                # 确保范围有效
                if start_week <= end_week and 1 <= start_week <= 30 and 1 <= end_week <= 30:
                    range_weeks = list(range(start_week, end_week + 1))
                    weeks.extend(range_weeks)
                    print(f"      添加周数: {range_weeks}")
                else:
                    print(f"      范围无效，跳过")
            except ValueError as e:
                print(f"      解析范围失败: {e}")
                continue
        else:
            # 单个周数
            print(f"      单个数字格式")
            try:
                week_num = int(part.strip())
                if 1 <= week_num <= 30:
                    weeks.append(week_num)
                    print(f"      添加周数: {week_num}")
                else:
                    print(f"      周数超出范围: {week_num}")
            except ValueError as e:
                print(f"      解析数字失败: {e}")
                continue
    
    # 去重并排序
    final_weeks = sorted(list(set(weeks)))
    print(f"    最终结果: {final_weeks}")

if __name__ == "__main__":
    test_weeks_parsing()

