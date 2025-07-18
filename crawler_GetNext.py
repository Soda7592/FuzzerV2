from selenium import webdriver
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
import subprocess
import requests

UrlQueue = []
VisitedUrl = []
PathsApi = {}
PathsPath = {}
ProxyHost = "http://127.0.0.1"
ProxyPort = 8080

# ---- Mitmproxy ----
# MitmProxyHost = "127.0.0.1"
# MitmProxyPort = 8080
# MitmAddon = "proxy/api_collector_addon.py"
# MitmWebApiPort = 8081
# MitmWebApiUrl = f"http://{MitmProxyHost}:{MitmWebApiPort}/api/requests"

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
    print(f"{Fore.RED}Waiting for 2 seconds for website fully render.{Style.RESET_ALL}")
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

def ClickByXpath(driver, xpath, timeout=5):
    print(f"{Fore.BLUE}Clicking by Xpath: {Fore.RED} {xpath} {Style.RESET_ALL}")
    try:
        target = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        target.click()
        print(f"{Fore.GREEN}Clicked by Xpath: {Fore.RED} {xpath} {Style.RESET_ALL}")
        return True
    except TimeoutException:
        print(f"{Fore.RED}[!] Timeout: {xpath} {Style.RESET_ALL}")
        return False
    except NoSuchElementException:
        print(f"{Fore.RED}[!] No such element: {xpath} {Style.RESET_ALL}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def GetPotentialInteractive(driver, RootUrl, AllTags):
    print(f"{Fore.GREEN}Getting Potential Interactive...{Style.RESET_ALL}")
    # KeyWords = ["submit", "save", "update", "edit", "delete", "add", "new", "create", 
    #     "confirm", "ok", "next", "send", "post", "search", "filter", "login",
    #     "btn", "button", "action", "link", "panel", "modal", "dialog", "item"]
    RootDomain = GetDomainName(RootUrl)
    # print(AllTags)
    for tag in AllTags:
        if tag.get("onclick",""):
            path = driver.current_url
            PathsApi[path] = None
            if tag.get("href") == "#":
                continue
            xpath = GetXpath(tag)
            ClickByXpath(driver, xpath)
            PathsApi[path] = {driver.current_url:""}
            if driver.current_url != path and GetUrlPath(driver.current_url, RootDomain) not in VisitedUrl:
                UrlQueue.append(driver.current_url)
                VisitedUrl.append(GetUrlPath(driver.current_url, RootDomain))
                print(f"{Fore.RED}BTN Find New Url! {Fore.YELLOW} Append visited url: {Fore.RED} {GetUrlPath(driver.current_url, RootDomain)} {Style.RESET_ALL}")
    

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
    if path[0] != "/":
        path = "/" + path
    if "http" in path:
        path = GetUrlPath(path, RootDomain)
    if "http" in RootUrl:
        if RootUrl[4] == "s":
            return "https://" + RootDomain + path
        else:
            return "http://" + RootDomain + path

# 應該要用 urljoin()，不然自己寫頭會破
# 問題在 HTML 瀏覽器的絕對路徑和相對路徑
# 有的時候 href 會寫成 href = "/administrator/index.php" 這種是絕對路徑
# 有的時候 href 會寫成 href = "index.php" 這種是相對路徑，這表示說把這個 url 加到 current url 的後面
# 例如 current_url 為 http://mtsec.dev/adminiatrator/ 那相對路徑就會變成 http://mtsec.dev/adminiatrator/index.php

# 我的 case 在處理相對路徑時會出錯，看看有沒有辦法用 urljoin() 來處理


def GetStaticUrl(driver, AllTags, RootUrl):
    RootDomain = GetDomainName(RootUrl)
    path = driver.current_url
    if path not in PathsPath:
        PathsPath[path] = []
    for tag in AllTags:
        if tag.name == "a": # and tag.get("href") not in VisitedUrl and tag.get("href") != None:
            t = GetUrlPath(tag.get("href"), RootDomain)
            if t != None and t[0] != "/" and t[0] != "#":
                t = GetUrlPath(path + t, RootDomain)
            if t not in VisitedUrl and t != None: 
                if ("http" in t or "https" in t) and t != None and t != "" and t[0] != "#":
                    UrlQueue.append(GetMergeUrl(RootUrl, RootDomain, t))
                    PathsPath[path].append(t)
                    print(f"{Fore.RED}Find New Url! {Fore.YELLOW} Append visited url: {Fore.RED} {t} {Style.RESET_ALL}")
                    VisitedUrl.append(t)
                    # print(GetMergeUrl(RootUrl, RootDomain, t))
                elif "http" not in t and "https" not in t and t != None and t != "" and t[0] != "#":
                    # if(t[0] == "#") :
                    #     continue 
                    UrlQueue.append(GetMergeUrl(RootUrl, RootDomain, t))
                    PathsPath[path].append(t)
                    print(f"{Fore.RED}Find New Url! {Fore.YELLOW} Append visited url: {Fore.RED} {t} {Style.RESET_ALL}")
                    VisitedUrl.append(t)
                # print(GetMergeUrl(RootUrl, RootDomain, t))
        elif tag.find("a"): # and tag.find("a").get("href") not in VisitedUrl and tag.find("a").get("href") != None:
            t = GetUrlPath(tag.find("a").get("href"), RootDomain)
            if t != None and t[0] != "/" and t[0] != "#":
                t = GetUrlPath(path + t, RootDomain)
            if t not in VisitedUrl and t != None:
                if ("http" in t or "https" in t) and t != None and t != "" and t[0] != "#":
                    UrlQueue.append(GetMergeUrl(RootUrl, RootDomain, t))
                    PathsPath[path].append(t)
                    print(f"{Fore.RED}Find New Url! {Fore.YELLOW} Append visited url: {Fore.RED} {t} {Style.RESET_ALL}")
                    VisitedUrl.append(t)
                    # print(GetMergeUrl(RootUrl, RootDomain, t))
                elif "http" not in t and "https" not in t and t != None and t != "" and t[0] != "#":
                    # if(t[0] == "#") :
                    #     continue
                    UrlQueue.append(GetMergeUrl(RootUrl, RootDomain, t))
                    PathsPath[path].append(t)
                    print(f"{Fore.RED}Find New Url! {Fore.YELLOW} Append visited url: {Fore.RED} {t} {Style.RESET_ALL}")
                    VisitedUrl.append(t)
                    # print(GetMergeUrl(RootUrl, RootDomain, t))
    # PrintUrlQueue(UrlQueue)
    return UrlQueue

def PrintUrlQueue(UrlQueue):
    for url in UrlQueue:
        print(url)

def GetNext(driver, RootUrl, url):
    print(f"{Fore.GREEN}\nGetting Next Url: {Fore.RED} {url} {Style.RESET_ALL}") 
    driver.get(url)
    time.sleep(3)
    AllTags = GetAllTags(driver)
    GetStaticUrl(driver, AllTags, url)
    GetPotentialInteractive(driver, RootUrl, AllTags)
    

def main(RootUrl, LoginUrl):
    # MitmProcess = None
    driver = None
    try:
        # MitmProcess = StartMitmProxy(MitmAddon)
        driver = UrlInit(RootUrl)
        GetLoginSession(driver, LoginUrl)
        # AllTags = GetAllTags(driver)
        GetNext(driver, RootUrl, RootUrl)
        # VisitedUrl.append(RootUrl)
        i = 0
        while len(UrlQueue)-1 > i :
            GetNext(driver, RootUrl, UrlQueue[i])
            i+=1
            print(f"{Fore.GREEN}Get Next Url: {Fore.RED} {UrlQueue[i]} {Style.RESET_ALL}")
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
    print("\n\nPathsAPIs:")
    for path in PathsApi:
        print(f"{Fore.BLUE}[*]{path}{Style.RESET_ALL}")
        print(f"{Fore.RED}{PathsApi[path]}{Style.RESET_ALL}")
    print("\n\nPathspath:")
    for path in PathsPath:
        print(f"{Fore.BLUE}[*]{path}{Style.RESET_ALL}")
        print(f"{Fore.RED}{PathsPath[path]}{Style.RESET_ALL}")
    

if __name__ == "__main__":
    RootUrl = "http://192.168.11.129:8080/index.php"
    LoginUrl = "http://192.168.11.129:8080/administrator"
    # print(GetDomainName("https://www.joomla.org"))
    init(autoreset=True)
    main(RootUrl, LoginUrl)
    
