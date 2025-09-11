from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from colorama import Fore, Back, Style, init
from urllib.parse import urljoin, urlparse
import datetime
import json
import os
import atexit
import signal
import sys
from collections import deque
from requests_handler import ApiSessionHandler
from ParseArg import ParseBody
from AnalyseInput import BuildData

UrlQueue = []
VisitedUrl = set()
ParentMap = {}
# UrlToApis = {}
UrlToNode = {}
node_dict = {}
PathsApi = {}
TotalApi = set()
PathsPath = {}
ProxyHost = "http://127.0.0.1"
ProxyPort = 8080
EXCLUDE_KEYWORDS = {"logout", "install", "installer", "plugin"}
# 控制是否顯示詳細除錯資訊
VERBOSE = False

# 進度統計：已處理 URL 數量
ProcessedCount = 0
MAX_PROCESSED = 100
RootStartUrl = None

# 取消樹狀圖資料結構，採線性紀錄

def debug(message):
    if VERBOSE:
        print(message)

# def ensure_node(url):
#     if url is None:
#         return
#     if url not in CrawlerTree:
#         CrawlerTree[url] = {"apis": [], "children": []}

# def add_edge(parent_url, child_url):
#     if parent_url is None or child_url is None:
#         return
#     ensure_node(parent_url)
#     ensure_node(child_url)
#     if child_url not in CrawlerTree[parent_url]["children"]:
#         CrawlerTree[parent_url]["children"].append(child_url)

# def add_api_to_node(url, api_info):
#     ensure_node(url)
#     normalized = dict(api_info)
#     headers_val = normalized.get("headers")
#     if isinstance(headers_val, dict):
#         normalized["headers"] = {str(k): str(v) for k, v in headers_val.items()}
#     else:
#         try:
#             normalized["headers"] = {str(k): str(v) for k, v in headers_val.items()}
#         except Exception:
#             normalized["headers"] = str(headers_val)
#     body_val = normalized.get("body")
#     if isinstance(body_val, (bytes, bytearray)):
#         try:
#             normalized["body"] = body_val.decode("utf-8", errors="ignore")
#         except Exception:
#             normalized["body"] = str(body_val)
#     CrawlerTree[url]["apis"].append(normalized)

def GetLoginSession(driver, LoginUrl):
    driver.get(LoginUrl)
    time.sleep(2)
    username = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "mod-login-username")))
    password = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "mod-login-password")))
    username.send_keys("user")
    password.send_keys("password")
    button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn.btn-primary.btn-block.btn-large.login-button")))
    button.click()
    time.sleep(3)
    print(f"{Fore.GREEN}Login Success{Style.RESET_ALL}")
    debug(f"{Fore.RED}Waiting for 2 seconds for website fully render.{Style.RESET_ALL}")
    time.sleep(2)

def GetXpath(input_tag):
    path = []
    el = input_tag
    for parent in el.parents:
        if parent is None or parent.name is None:
            break
        siblings_of_same_name = [s for s in parent.children if s.name == el.name]
        if len(siblings_of_same_name) > 1:
            count = 1
            for sibling in parent.children:
                if sibling == el:
                    path.append(f"{el.name}[{count}]")
                    break
                if sibling.name == el.name:
                    count += 1
        else:
            path.append(el.name)
        el = parent
    return '/' + '/'.join(reversed(path))

def RequestsCheck(driver, url):
    requests = driver.requests
    Domain = GetDomainName(url)
    ApiList = []
    for request in requests:
        url = request.url.rstrip("/")
        if request.method == 'POST' and Domain in url and url not in TotalApi:
            try:
                headers_dict = {str(k): str(v) for k, v in request.headers.items()}
            except Exception:
                headers_dict = str(request.headers)
            body_text = request.body.decode("utf-8", errors="ignore") if isinstance(request.body, (bytes, bytearray)) else str(request.body)
            api_info = {
                "url": str(url),
                "method": str(request.method),
                "headers": headers_dict,
                "body": body_text
            }
            ApiList.append(api_info)
            TotalApi.add(url)
    return ApiList

def ClickByXpath(driver, xpath, timeout=1):
    debug(f"{Fore.BLUE}Clicking by Xpath: {Fore.RED} {xpath} {Style.RESET_ALL}")
    try:
        target = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        target.click()
        RequestList = RequestsCheck(driver, driver.current_url.rstrip("/"))
        if RequestList:
            return RequestList
        return None
    except TimeoutException:
        debug(f"{Fore.RED}[!] Timeout: {xpath} {Style.RESET_ALL}")
        return None
    except NoSuchElementException:
        debug(f"{Fore.RED}[!] No such element: {xpath} {Style.RESET_ALL}")
        return None
    except Exception as e:
        debug(f"Error: {e}")
        return None

def GetPotentialInteractive(driver, RootUrl, AllTags):
    debug(f"{Fore.GREEN}Getting Potential Interactive...{Style.RESET_ALL}")
    RootDomain = GetDomainName(RootUrl)
    for tag in AllTags:
        if tag.get("onclick",""):
            path = driver.current_url.rstrip("/")
            if path not in PathsApi:
                PathsApi[path] = {}
            if tag.get("href") == "#":
                continue
            xpath = GetXpath(tag)
            captured = ClickByXpath(driver, xpath)
            if captured is not None:
                for req in captured:
                    PathsApi[path][req['url']] = {"body":req['body'], "method":req['method'], "headers":req['headers']}
                    debug(f"captured api url: {req['url']}")
            if driver.current_url != path and driver.current_url not in VisitedUrl:
                new_url = driver.current_url.rstrip("/")
                if IsHttpUrl(new_url) and not should_exclude_url(new_url):
                    UrlQueue.append(new_url)
                    VisitedUrl.add(new_url)
                    ParentMap[new_url] = path
                    debug(f"{Fore.RED}Find New Url! {Fore.YELLOW} Append visited url: {Fore.RED} {new_url} {Style.RESET_ALL}")

def UrlInit(RootUrl):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(RootUrl)
        VisitedUrl.add(RootUrl)
        ParentMap[RootUrl] = None
        time.sleep(2)
        username = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "modlgn-username")))
        password = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "modlgn-passwd")))
        username.send_keys("user")
        password.send_keys("password")
        button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "Submit")))
        button.click()
        time.sleep(2)
        print(f"{Fore.GREEN}Login Success{Style.RESET_ALL}")
        print(f"{Fore.RED}Waiting for 2 seconds for website fully render.{Style.RESET_ALL}")

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

def GetDomainName(url):
    if "http" in url or "https" in url:
        start = url.find("//")
        end = url.find("/", start + 2)
        if end == -1:
            return url[start + 2:]
        return url[start + 2:end]
    else:
        return url

def GetUrlPath(url, RootDomain):
    if url is None:
        return None
    elif "http" in url or "https" in url:
        DomainName = GetDomainName(url)
        if DomainName != RootDomain:
            return None
        start = url.find("//")
        end = url.find("/", start + 2)
        if end == -1:
            return url[start + 2:]
        else:
            return url[end:]
    else:
        return url

def GetMergeUrl(current, path):
    return urljoin(current, path)

def should_exclude_url(url):
    if not url:
        return False
    lower_url = str(url).lower()
    for kw in EXCLUDE_KEYWORDS:
        if kw.lower() in lower_url:
            return True
    return False

def IsHttpUrl(url):
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https")
    except Exception:
        return False

def GetStaticUrl(driver, AllTags, RootUrl):
    RootDomain = GetDomainName(RootUrl)
    path = driver.current_url.rstrip("/")
    if path not in PathsPath:
        PathsPath[path] = []
    for tag in AllTags:
        if tag.name == "a":
            href_val = tag.get("href")
            if should_exclude_url(href_val):
                continue
            t = GetUrlPath(href_val, RootDomain)
            if t and t[0] != "#":
                url = GetMergeUrl(path, t).rstrip("/")
                if url not in VisitedUrl and url and not should_exclude_url(url) and IsHttpUrl(url):
                    debug(f"{Fore.RED}Find New Url! {Fore.YELLOW} Append visited url: {Fore.RED} {url} {Style.RESET_ALL}")
                    UrlQueue.append(url)
                    PathsPath[path].append(t)
                    VisitedUrl.add(url)
                    ParentMap[url] = path
        elif tag.find("a"):
            href_val = tag.find("a").get("href")
            if should_exclude_url(href_val):
                continue
            t = GetUrlPath(href_val, RootDomain)
            if t and t[0] != "#":
                url = GetMergeUrl(path, t).rstrip("/")
                if url not in VisitedUrl and url and not should_exclude_url(url) and IsHttpUrl(url):
                    debug(f"{Fore.RED}Find New Url! {Fore.YELLOW} Append visited url: {Fore.RED} {url} {Style.RESET_ALL}")
                    UrlQueue.append(url)
                    PathsPath[path].append(t)
                    VisitedUrl.add(url)
                    ParentMap[url] = path
    return UrlQueue

def PrintUrlQueue(UrlQueue):
    for url in UrlQueue:
        print(url)

def GetNext(driver, RootUrl, url):
    global ProcessedCount
    ProcessedCount += 1
    pending = max(len(UrlQueue) - ProcessedCount, 0)
    print(f"{Fore.GREEN}Processing (done/pending) {ProcessedCount}/{pending}: {Style.RESET_ALL}  {Fore.RED}{url}{Style.RESET_ALL}")
    # 線性處理，不建樹
    driver.get(url)
    time.sleep(3)
    AllTags = GetAllTags(driver)
    GetStaticUrl(driver, AllTags, url)
    GetPotentialInteractive(driver, RootUrl, AllTags)

    # if ProcessedCount % 50 == 0:
    #     print(f"{Fore.YELLOW}Periodic save at {ProcessedCount}{Style.RESET_ALL}")
    #     Save(root_url=RootStartUrl, filename=GetTime())
    if ProcessedCount >= MAX_PROCESSED:
        print(f"{Fore.YELLOW}Reached limit {MAX_PROCESSED}, saving and exiting...{Style.RESET_ALL}")
        # Save(root_url=RootStartUrl)
        raise SystemExit(0)

def GetTime():
    now = datetime.datetime.now()
    filename = now.strftime("%Y_%m_%d_%H") + ".json"
    return filename

def Save():
    try:
        filename = GetTime()
        abs_path = os.path.abspath(filename)
        BuildUrlToNode()
        with open(abs_path, 'w', encoding='utf-8') as f:
            json.dump(UrlToNode["http://192.168.11.129:8080/index.php"], f, ensure_ascii=False, indent=2)
        print(f"{Fore.GREEN}Saved data to {abs_path}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Save failed: {e}{Style.RESET_ALL}")

def safe_save():
    try:
        Save()
    except Exception as e:
        print(f"{Fore.RED}Safe save failed: {e}{Style.RESET_ALL}")

def handle_interrupt(sig, frame):
    # TestPrentMap()
    print(f"\n{Fore.YELLOW}Received interrupt signal, saving data...{Style.RESET_ALL}")
    safe_save()
    sys.exit(0)

def TestPrentMap():
    for url in ParentMap:
        print(f"{Fore.RED}url: {url}{Style.RESET_ALL} \n-> {Fore.YELLOW}Parent: {ParentMap[url]}{Style.RESET_ALL}\n")

def BuildUrlToNode():
    for url in ParentMap:
        UrlToNode[url] = {"url":url, "children":[]}
    for url, parent in ParentMap.items():
        if parent is not None:
            UrlToNode[parent]["children"].append(UrlToNode[url])
    # for url in UrlToNode:
    #     print(f"{Fore.RED}{url}{Style.RESET_ALL} \n-> {Fore.YELLOW}Children: {UrlToNode[url]['children']}{Style.RESET_ALL}\n")

def main(RootUrl, LoginUrl):
    # global RootStartUrl
    # RootStartUrl = RootUrl  # 明確設定根為 index.php
    signal.signal(signal.SIGINT, handle_interrupt)
    signal.signal(signal.SIGTERM, handle_interrupt)
    atexit.register(safe_save)
    VisitedUrl.add("http://192.168.11.129:8080")
    VisitedUrl.add("http://192.168.11.129:8080/")
    driver = None
    try:
        driver = UrlInit(RootUrl)
        GetLoginSession(driver, LoginUrl)
        GetNext(driver, RootUrl, RootUrl)
        i = 0
        while i < len(UrlQueue):
            GetNext(driver, RootUrl, UrlQueue[i])
            i += 1
            debug(f"{Fore.GREEN}Get Next Url: {Fore.RED} {UrlQueue[i] if i < len(UrlQueue) else 'End'}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Done{Style.RESET_ALL}")
    except SystemExit:
        pass
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        # Save(root_url=RootStartUrl)
    finally:
        if driver:
            driver.close()
            print(f"{Fore.GREEN}Driver closed.{Style.RESET_ALL}")
            # TestUrlToNode()
            #TestPrentMap()

if __name__ == "__main__":
    RootUrl = "http://192.168.11.129:8080/index.php"
    LoginUrl = "http://192.168.11.129:8080/administrator"
    init(autoreset=True)
    main(RootUrl, LoginUrl)