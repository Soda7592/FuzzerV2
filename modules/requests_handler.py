import requests
import json
from colorama import Fore, Style, init
from bs4 import BeautifulSoup
from urllib.parse import urlparse
root_domain = "192.168.11.129:8080"
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
        while True:
            try:
                # 使用 self.session.request 發送請求，它會自動帶上 cookies
                response = self.session.request(
                    method,
                    url,
                    headers=headers,
                    data=data,
                    timeout=10, # 設置超時
                    allow_redirects=False
                )
                print(f"{Fore.BLUE}requesting: : {method} {url}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}Success: {response.status_code}{Style.RESET_ALL}")
                if 300 <= response.status_code < 400:
                    next_url = response.headers.get('Location')
                    if next_url:
                        parsed_next_url = urlparse(next_url)
                        if parsed_next_url.netloc != root_domain:
                            return response
                        url = next_url
                        print(f"{Fore.BLUE}redirecting: {next_url}{Style.RESET_ALL}")
                        continue
                    return response
                return response
            
            except requests.exceptions.RequestException as e:
                print(f"{Fore.RED}API Request Failed: {e}{Style.RESET_ALL}")
                return None
    
    