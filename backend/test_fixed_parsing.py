#!/usr/bin/env python3
"""
测试修复后的周数解析功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import parse_weeks

def test_fixed_parsing():
    """测试修复后的周数解析"""
    print("🔍 测试修复后的周数解析功能")
    print("=" * 50)
    
    # 测试您遇到的具体问题
    test_cases = [
        ("4-18周", [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]),
        ("第4-18周", [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]),
        ("1-16周", list(range(1, 17))),
        ("1,4-6,9", [1, 4, 5, 6, 9]),
        ("1-5,8-10", [1, 2, 3, 4, 5, 8, 9, 10]),
        ("6-9周", [6, 7, 8, 9]),
        ("1,3,5", [1, 3, 5]),
        ("4-18", [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]),  # 不带"周"
    ]
    
    all_passed = True
    
    for i, (input_str, expected) in enumerate(test_cases, 1):
        print(f"\n测试 {i}: '{input_str}'")
        result = parse_weeks(input_str)
        print(f"  期望结果: {expected}")
        print(f"  实际结果: {result}")
        
        if result == expected:
            print(f"  ✅ 通过")
        else:
            print(f"  ❌ 失败")
            all_passed = False
    
    print(f"\n{'='*50}")
    if all_passed:
        print("🎉 所有测试通过！周数解析功能已修复")
    else:
        print("❌ 部分测试失败，需要进一步调试")
    
    # 特别测试您遇到的问题
    print(f"\n🔍 特别测试您的具体问题:")
    problem_case = "4-18周"
    result = parse_weeks(problem_case)
    print(f"输入: '{problem_case}'")
    print(f"解析结果: {result}")
    print(f"结果长度: {len(result)}")
    
    if len(result) > 0:
        print("✅ 问题已解决！现在可以正确解析周数了")
    else:
        print("❌ 问题仍然存在，需要进一步调试")

if __name__ == "__main__":
    test_fixed_parsing()

