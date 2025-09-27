import requests
import base64
import time
import os
from bs4 import BeautifulSoup
from PIL import Image
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import json

# =================================================================================
#  用户配置区域 - 请在这里修改您的信息
# =================================================================================
STUDENT_ID = "202311000516"  # <--- 在这里替换为你的学号
PASSWORD = "Youzicha0213@"   # <--- 在这里替换为你的原始明文密码
# =================================================================================


class JwxtLogin:
    def __init__(self, student_id, password):
        self.student_id = student_id
        self.password = password
        self.session = requests.Session()
        self.base_url = "http://jwxt.sdnu.edu.cn/jwglxt"
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0'
        })

    def _get_csrf_token(self):
        print("[1] 正在访问登录页面以获取csrftoken...")
        try:
            login_page_url = f"{self.base_url}/xtgl/login_slogin.html"
            resp = self.session.get(login_page_url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            token_element = soup.find('input', {'id': 'csrftoken'})
            if token_element: return token_element.get('value')
            return None
        except Exception: return None

    def _get_encrypted_password(self):
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
        print("[4] 正在获取验证码...")
        try:
            timestamp = int(time.time() * 1000)
            captcha_url = f"{self.base_url}/kaptcha?time={timestamp}"
            resp = self.session.get(captcha_url)
            resp.raise_for_status()
            with open("captcha.jpg", "wb") as f: f.write(resp.content)
            print("    -> 验证码已保存为 captcha.jpg，请查看。")
            try: Image.open("captcha.jpg").show()
            except Exception: print("    -> (提示: 自动打开图片失败, 请手动打开 captcha.jpg)")
            captcha_code = input("    -> 请输入您看到的验证码: ")
            os.remove("captcha.jpg")
            return captcha_code
        except Exception as e:
            print(f"    -> [错误] 获取验证码失败: {e}")
            return None

    def login(self):
        """最终的、决定性的登录流程"""
        csrftoken = self._get_csrf_token()
        if not csrftoken: 
            print("[错误] 步骤1失败: 无法获取csrftoken。")
            return False

        encrypted_password = self._get_encrypted_password()
        if not encrypted_password: return False
        
        captcha_code = self._get_captcha_code()
        if not captcha_code: return False

        print("[5] 正在提交登录请求...")
        login_post_url = f"{self.base_url}/xtgl/login_slogin.html"
        payload = {
            'csrftoken': csrftoken, 'yhm': self.student_id, 'mm': encrypted_password,
            'yzm': captcha_code, 'language': 'zh_CN', 'ydType': 'yhm'
        }
        
        try:
            resp_login = self.session.post(login_post_url, data=payload)
            resp_login.raise_for_status()
            
            # ======================= 这是最终的、正确的判断逻辑 =======================
            # 成功的标志是服务器发生了重定向 (response.history不为空)。
            # 这意味着POST请求被接受了，服务器让我们跳转到下一个页面（通知页）。
            if resp_login.history:
                print("[6] ✅ POST请求成功，服务器已重定向！正在进入主系统...")
                
                # 步骤7: 模拟点击“已阅读”后的跳转，进入主界面
                index_url = f"{self.base_url}/xtgl/login_loginIndex.html"
                self.session.get(index_url)
                print("[7] ✅ 成功进入主系统！登录流程全部完成。")
                return True
            else:
                # 如果没有发生重定向，说明POST请求被拒绝，停留在登录页。
                if "用户名或密码不正确" in resp_login.text:
                     print("[6] ❌ 登录失败: 用户名或密码不正确！")
                elif "验证码输入错误" in resp_login.text:
                     print("[6] ❌ 登录失败: 验证码输入错误！")
                else:
                    # 如果返回的还是登录页，但没有明确提示，大概率还是验证码错了
                    print("[6] ❌ 登录失败: 验证码很可能输入错误。")
                return False
            # ======================================================================

        except requests.exceptions.RequestException as e:
            print(f"    -> [错误] 提交登录请求时失败: {e}")
            return False

    def get_schedule(self, year, term):
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

if __name__ == '__main__':
    if "YOUR_STUDENT_ID" in STUDENT_ID or "YOUR_ORIGINAL_PASSWORD" in PASSWORD:
        print("!!! 请先在脚本顶部的'用户配置区域'填入您的学号和密码。")
    else:
        jwxt = JwxtLogin(STUDENT_ID, PASSWORD)
        is_logged_in = jwxt.login()
        
        if is_logged_in:
            schedule_data = jwxt.get_schedule(year=2025, term=1)
            if schedule_data:
                kb_list = schedule_data.get('kbList', [])
                print(f"\n--- 课表信息 ---")
                print(f"共获取到 {len(kb_list)} 门课程安排。")
                print(json.dumps(schedule_data, indent=2, ensure_ascii=False))
                print("="*70)