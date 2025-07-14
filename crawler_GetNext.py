from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from colorama import Fore, Back, Style, init
import subprocess
import requests

UrlQueue = []
VisitedUrl = []
ProxyHost = "http://127.0.0.1"
ProxyPort = 8080

# ---- Mitmproxy ----
# MitmProxyHost = "127.0.0.1"
# MitmProxyPort = 8080
# MitmAddon = "proxy/api_collector_addon.py"
# MitmWebApiPort = 8081
# MitmWebApiUrl = f"http://{MitmProxyHost}:{MitmWebApiPort}/api/requests"

def GetXpath(input_tag): # 將參數名改為 input_tag 更清晰
    path = []
    el = input_tag # 在這裡複製一份，用 el 來遍歷，不改變原始 input_tag

    for parent in el.parents: # 遍歷 el 的所有祖先
        if parent is None or parent.name is None: # 判斷是否到達文檔根部或無效父節點
            break
        
        # 獲取當前元素 el 在其父元素 parent 下的所有同名兄弟元素
        siblings_of_same_name = [s for s in parent.children if s.name == el.name]
        
        # 如果有多個同名兄弟元素，需要添加索引來區分
        if len(siblings_of_same_name) > 1:
            count = 1
            # 遍歷父元素的所有子元素，找到當前元素 el 是同名兄弟中的第幾個
            for sibling in parent.children:
                if sibling == el: # 找到當前元素
                    path.append(f"{el.name}[{count}]")
                    break # 找到後跳出內層循環
                if sibling.name == el.name: # 如果是同名兄弟，計數器加一
                    count += 1
        else:
            # 如果只有一個同名兄弟，則不需要索引
            path.append(el.name)
        
        el = parent # 移動到父元素，繼續向上遍歷
            
    # 將路徑反轉（因為我們是從下往上構建的），然後用 '/' 連接，並在最前面加上 '/'
    return '/' + '/'.join(reversed(path))

def GetPotentialInteractive(AllTags):
    print(f"{Fore.GREEN}Getting Potential Interactive...{Style.RESET_ALL}")
    KeyWords = ["submit", "save", "update", "edit", "delete", "add", "new", "create", 
        "confirm", "ok", "next", "send", "post", "search", "filter", "login",
        "btn", "button", "action", "link", "panel", "modal", "dialog", "item"]
    
    # print(AllTags)

    for tag in AllTags:
        if tag.get("onclick",""):
            if tag.get("href") == "#":
                continue
            print(GetXpath(tag))
    

def UrlInit(RootUrl):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        # chrome_options.add_argument(f"--proxy-server={ProxyHost}:{ProxyPort}")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(RootUrl)
        VisitedUrl.append(GetUrlPath(RootUrl, GetDomainName(RootUrl)))
        # FullHTML = driver.page_source
        time.sleep(2)
        username = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "modlgn-username")))
        password = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "modlgn-passwd")))
        username.send_keys("user")
        password.send_keys("password")
        button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "Submit")))
        button.click()
        time.sleep(3)
        # while(FullHTML == driver.page_source):
        #     time.sleep(1)
        #     FullHTML = driver.page_source
        print(f"{Fore.GREEN}Login Success{Style.RESET_ALL}")
        print(f"{Fore.RED}Waiting for 2 seconds for website fully render.{Style.RESET_ALL}")
        time.sleep(2)
        return driver
    except Exception as e:
        print(f"Error: {e}")

def GetAllTags(driver):
    try:
        FullHTML = driver.page_source
        soup = BeautifulSoup(FullHTML, "html.parser")
        AllTags = soup.find_all()
        return AllTags
    except Exception as e:
        print(f"Error: {e}")
    

def GetDomainName(url) :
    if "http" in url or "https" in url:
        start = url.find("//")
        end = url.find("/", start + 2) # Find slash and start from start+2 index.
        if end == -1:
            return url[start + 2:]
        return url[start + 2:end]
    else:
        return url

def GetUrlPath(url, RootDomain) :
    if url == None:
        return None
    elif "http" in url or "https" in url:
        DomainName = GetDomainName(url)
        if DomainName != RootDomain:
            return None
        start = url.find("//")
        end = url.find("/", start + 2) # Find slash and start from start+2 index.
        if end == -1:
            return url[start + 2:]
        else:
            return url[end:]
    else:
        return url

def GetMergeUrl(RootUrl, RootDomain, path):
    if "http" in path:
        path = GetUrlPath(path, RootDomain)
    if "http" in RootUrl:
        if RootUrl[4] == "s":
            return "https://" + RootDomain + path
        else:
            return "http://" + RootDomain + path

def GetStaticUrl(AllTags, RootUrl):
    RootDomain = GetDomainName(RootUrl)
    for tag in AllTags:
        if tag.name == "a": # and tag.get("href") not in VisitedUrl and tag.get("href") != None:
            t = GetUrlPath(tag.get("href"), RootDomain)
            if t not in VisitedUrl and t != None: 
                if ("http" in t or "https" in t) and t != None and t != "" and t[0] != "#":
                    UrlQueue.append(GetMergeUrl(RootUrl, RootDomain, t))
                    print(f"{Fore.RED}Find New Url! {Fore.YELLOW} Append visited url: {Fore.RED} {t} {Style.RESET_ALL}")
                    VisitedUrl.append(t)
                    # print(GetMergeUrl(RootUrl, RootDomain, t))
                elif "http" not in t and "https" not in t and t != None and t != "" and t[0] != "#":
                    # if(t[0] == "#") :
                    #     continue 
                    UrlQueue.append(GetMergeUrl(RootUrl, RootDomain, t))
                    print(f"{Fore.RED}Find New Url! {Fore.YELLOW} Append visited url: {Fore.RED} {t} {Style.RESET_ALL}")
                    VisitedUrl.append(t)
                # print(GetMergeUrl(RootUrl, RootDomain, t))
        elif tag.find("a"): # and tag.find("a").get("href") not in VisitedUrl and tag.find("a").get("href") != None:
            t = GetUrlPath(tag.find("a").get("href"), RootDomain)
            if t not in VisitedUrl and t != None:
                if ("http" in t or "https" in t) and t != None and t != "" and t[0] != "#":
                    UrlQueue.append(GetMergeUrl(RootUrl, RootDomain, t))
                    print(f"{Fore.RED}Find New Url! {Fore.YELLOW} Append visited url: {Fore.RED} {t} {Style.RESET_ALL}")
                    VisitedUrl.append(t)
                    # print(GetMergeUrl(RootUrl, RootDomain, t))
                elif "http" not in t and "https" not in t and t != None and t != "" and t[0] != "#":
                    # if(t[0] == "#") :
                    #     continue
                    UrlQueue.append(GetMergeUrl(RootUrl, RootDomain, t))
                    print(f"{Fore.RED}Find New Url! {Fore.YELLOW} Append visited url: {Fore.RED} {t} {Style.RESET_ALL}")
                    VisitedUrl.append(t)
                    # print(GetMergeUrl(RootUrl, RootDomain, t))
    PrintUrlQueue(UrlQueue)
    return UrlQueue

def PrintUrlQueue(UrlQueue):
    for url in UrlQueue:
        print(url)

def GetNext(driver, url):
    print(f"{Fore.GREEN}\nGetting Next Url: {Fore.RED} {url} {Style.RESET_ALL}") 
    driver.get(url)
    time.sleep(3)
    AllTags = GetAllTags(driver)
    GetPotentialInteractive(AllTags)
    GetStaticUrl(AllTags, url)

def main(RootUrl):
    # MitmProcess = None
    driver = None
    try:
        # MitmProcess = StartMitmProxy(MitmAddon)
        driver = UrlInit(RootUrl)
        AllTags = GetAllTags(driver)
        UrlQueue = GetStaticUrl(AllTags, RootUrl)
        for i in range(len(UrlQueue)):
            GetNext(driver, UrlQueue[i])
        print(f"{Fore.GREEN}Done{Style.RESET_ALL}")
        for i in range(len(VisitedUrl)):
            print(VisitedUrl[i])
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
    finally:
        if driver:
            driver.close()
            print(f"{Fore.GREEN}Driver closed.{Style.RESET_ALL}")
        # if MitmProcess:
        #     StopMitmProxy(MitmProcess)
    

if __name__ == "__main__":
    RootUrl = "http://192.168.11.129:8080/index.php"
    # print(GetDomainName("https://www.joomla.org"))
    init(autoreset=True)
    main(RootUrl)
    
