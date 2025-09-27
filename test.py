import requests
import json # 引入json库，方便格式化输出

# 1. 目标 URL
url = "http://jwxt.sdnu.edu.cn/jwglxt/kbcx/xskbcx_cxXsgrkb.html?gnmkdm=N253508"

# 2. 完整的请求头 (Headers)
# 从之前的截图中复制，只需替换Cookie
headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    # ===============================重要===================================
    # !!! 将这里的 JSESSIONID 换成您自己当前有效的 Cookie 值 !!!
    'Cookie': 'JSESSIONID=C8FF603AC16F26E64C9461E336E85B12', 
    # ======================================================================
    'Host': 'jwxt.sdnu.edu.cn',
    'Origin': 'http://jwxt.sdnu.edu.cn',
    'Referer': 'http://jwxt.sdnu.edu.cn/jwglxt/kbcx/xskbcx_cxXskbcxIndex.html?gnmkdm=N253508&layout=default',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0',
    'X-Requested-With': 'XMLHttpRequest'
}

# 3. 完整的请求体 (Payload / Form Data)
# 这就是您刚刚找到的数据
payload = {
    'xnm': '2025',
    'xqm': '3',
    'kzlx': 'ck',
    'xsdm': '' # 假设 xsdm 为空字符串，如果不是，请相应修改
}

# 4. 发送 POST 请求
try:
    response = requests.post(url, headers=headers, data=payload)
    # 检查请求是否成功
    response.raise_for_status() 

    # 5. 解析并打印返回的课表JSON数据
    # .json() 会自动将返回的 JSON 字符串解析为 Python 字典
    schedule_data = response.json()
    
    # 使用 json.dumps 进行格式化打印，使输出更美观
    print(json.dumps(schedule_data, indent=2, ensure_ascii=False))

except requests.exceptions.RequestException as e:
    print(f"请求失败: {e}")
    # 如果请求失败，可以打印出响应原文帮助排查问题
    # print(response.text)