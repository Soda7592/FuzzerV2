from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from collections import deque
import json
import time
from colorama import Fore, Style, init


ResourcesPool = "../ResourcesPool/"
tree = ""
with open(ResourcesPool + "tree.json", "r", encoding="utf-8") as f:
    tree = json.load(f)

def GetLoginSession():
    with open(ResourcesPool + "LoginSession.json", "r", encoding="utf-8") as f:
        return json.load(f)

override_script = """
(function() {
    window.__xss_markers = [];
    if (window === window.top) {
        window.addEventListener('message', function(event) {
            if (event.data && event.data.type === 'XSS_REPORT') {
                window.__xss_markers.push(event.data.msg);
            }
        });
    }

    const originalAlert = window.alert;
    window.alert = function(message) {
        const msg = String(message || '');
        
        console.log('[CUSTOM ALERT context: ' + window.location.href + '] ' + msg);
        
        if (window === window.top) {
            window.__xss_markers.push(msg);
        } else {
            window.top.postMessage({type: 'XSS_REPORT', msg: msg}, '*');
        }
    };

    window.getXssMarkers = function() {
        return window.__xss_markers;
    };
})();
"""

def BFS(tree) :
    queue = deque([tree])
    allUrls = []
    while queue:
        node = queue.popleft()
        currentUrl = node.get('url')
        if currentUrl:
            allUrls.append(currentUrl)
        children = node.get('children') 
        if children:
            for child in children:
                queue.append(child)
    return allUrls

if __name__ == "__main__":
    init(autoreset=True)
    loginSession = GetLoginSession()
    rootUrl = "http://192.168.11.129:8080"
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    if "UserAgent" in loginSession:
        chrome_options.add_argument(f"user-agent={loginSession['UserAgent']}")
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": override_script
    })
    driver.get(rootUrl)
    time.sleep(2)

    cookies = GetLoginSession()["Cookies"]
    for cookie in cookies:
        cookieDict = {
            'name': cookie['name'],
            'value': cookie['value'],
            'path': cookie['path'],
            'secure': cookie['secure']
        }
        try:
            driver.add_cookie(cookieDict)
            time.sleep(2)
            driver.refresh()
            time.sleep(2)
            driver.get('http://192.168.11.129:8080/administrator/')
            body = driver.page_source
            if(len(body) > 30000):
                print(f"{Fore.GREEN}Login Success{Style.RESET_ALL}")
            else :
                print(f"{Fore.RED}Login Failed{Style.RESET_ALL}")
        except Exception as e:
            print(f"加入 Cookie 失敗 ({cookieDict['name']}): {e}")

    
    print("")
    count = 0
    paths = BFS(tree)
    for url in paths:
        # === 測試範例 ===
        #driver.get("http://localhost:5500/Check/exampletest.html")  # 換成你的測試頁面
        driver.get(url)
        # 等待 JS 有機會執行
        time.sleep(1.5)
        # === 取得所有被呼叫的 alert 內容 ===

        alert_messages = driver.execute_script("return window.getXssMarkers() || [];")

        

        # === 正確判斷：只看有沒有包含你的 marker ===
        MY_MARKER = "a"   # 你可以隨機生成，例如 "XSS-114514-a7b9"

        if alert_messages:
            count += 1
            print("")
            print("觸發的 alert 內容：", alert_messages)
            print(f"{Fore.GREEN}{url} {Style.RESET_ALL}")
            print("XSS Confirmed!")
        else:
            print("")
            print(f"{Fore.RED}{url} {Style.RESET_ALL}")
            print("No alert detected.")
    print("")
    print(count)

        # for msg in alert_messages:
        #     if MY_MARKER in msg:
        #         print(f"{Fore.GREEN}{url} {Style.RESET_ALL}")
        #         break
        # else:
        #     print(f"{Fore.RED}{url} {Style.RESET_ALL}")
        #     print("Normal alert.")