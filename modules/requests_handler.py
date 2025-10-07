import requests
import json
from colorama import Fore, Style, init
from bs4 import BeautifulSoup

init(autoreset=True)

class ApiSessionHandler:
    def __init__(self, cookies):
        self.session = requests.Session()
        self.session_cookies = {c['name']: c['value'] for c in cookies}
        self.session.cookies.update(self.session_cookies)
        # print(f"{Fore.GREEN}ApiSessionHandler 已初始化，並載入 {len(self.session.cookies)} 個 Cookies。{Style.RESET_ALL}")
    
    def GetAllTagsFromRequest(self, url):
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        AllTags = soup.find_all()
        return AllTags
    
    def SendApiRequest(self, method, url, headers=None, data=None):
        if headers is None:
            headers = {}
        try:
            # 使用 self.session.request 發送請求，它會自動帶上 cookies
            response = self.session.request(
                method,
                url,
                headers=headers,
                data=data,
                timeout=10 # 設置超時
            )
            response.raise_for_status()
            print(f"{Fore.BLUE}發送請求: {method} {url}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}請求成功，狀態碼: {response.status_code}{Style.RESET_ALL}")
            # 如果狀態碼是 4xx 或 5xx，會拋出異常
            return response
            
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}API 請求失敗: {e}{Style.RESET_ALL}")
            return None
    
    