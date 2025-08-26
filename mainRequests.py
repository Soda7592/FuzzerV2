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
from urllib.parse import urljoin
import subprocess
from requests_handler import ApiSessionHandler
from ParseArg import ParseBody

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

def RequestsCheck(driver, url):
    requests = driver.requests
    Domain = GetDomainName(url)
    ApiList = []
    for request in requests:
        if request.method == 'POST' and Domain in request.url:
            # print(request.url)
            ApiList.append(request)
    return ApiList

def ClickByXpath(driver, xpath, timeout=1):
    # print(f"{Fore.BLUE}Clicking by Xpath: {Fore.RED} {xpath} {Style.RESET_ALL}")
    try:
        target = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        target.click()
        RequestList = RequestsCheck(driver, driver.current_url)
        if RequestList:
            return RequestList
        return None
    except TimeoutException:
        # print(f"{Fore.RED}[!] Timeout: {xpath} {Style.RESET_ALL}")
        return None
    except NoSuchElementException:
        print(f"{Fore.RED}[!] No such element: {xpath} {Style.RESET_ALL}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

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
            if path not in PathsApi:
                PathsApi[path] = {}
            if tag.get("href") == "#":
                continue
            xpath = GetXpath(tag)
            captured = ClickByXpath(driver, xpath)
            if captured is not None:
                for req in captured:
                    # print("captured: ", req)
                    PathsApi[path][req.url] = req.body.decode("utf-8")
            if driver.current_url != path and driver.current_url not in VisitedUrl:
                UrlQueue.append(driver.current_url)
                VisitedUrl.append(driver.current_url)
                print(f"{Fore.RED}Find New Url! {Fore.YELLOW} Append visited url: {Fore.RED} {driver.current_url} {Style.RESET_ALL}")

def UrlInit(RootUrl, LoginUrl):
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
        GetLoginSession(driver, LoginUrl)
        cookies = driver.get_cookies()
        return driver, cookies
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

def GetMergeUrl(current, path) :
    return urljoin(current, path)
# def GetMergeUrl(RootUrl, RootDomain, path):
#     if path[0] != "/":
#         path = "/" + path
#     if "http" in path:
#         path = GetUrlPath(path, RootDomain)
#     if "http" in RootUrl:
#         if RootUrl[4] == "s":
#             return "https://" + RootDomain + path
#         else:
#             return "http://" + RootDomain + path


def GetStaticUrl(driver, AllTags, RootUrl):
    RootDomain = GetDomainName(RootUrl)
    path = driver.current_url
    if path not in PathsPath:
        PathsPath[path] = []
    for tag in AllTags:
        if tag.name == "a": # and tag.get("href") not in VisitedUrl and tag.get("href") != None:
            t = GetUrlPath(tag.get("href"), RootDomain)
            if t != None and t[0] != "#" :
                url = GetMergeUrl(path, t)
                if url not in VisitedUrl and url != None:
                    print(f"{Fore.RED}Find New Url! {Fore.YELLOW} Append visited url: {Fore.RED} {url} {Style.RESET_ALL}")
                    UrlQueue.append(url)
                    PathsPath[path].append(t)
                    VisitedUrl.append(url)
            # if t != None and t[0] != "/" and t[0] != "#":
            #     t = GetUrlPath(path + t, RootDomain)
            # if t not in VisitedUrl and t != None: 
            #     if ("http" in t or "https" in t) and t != None and t != "" and t[0] != "#":
            #         UrlQueue.append(GetMergeUrl(RootUrl, RootDomain, t))
            #         PathsPath[path].append(t)
            #         print(f"{Fore.RED}Find New Url! {Fore.YELLOW} Append visited url: {Fore.RED} {t} {Style.RESET_ALL}")
            #         VisitedUrl.append(t)
            #         # print(GetMergeUrl(RootUrl, RootDomain, t))
            #     elif "http" not in t and "https" not in t and t != None and t != "" and t[0] != "#":
            #         # if(t[0] == "#") :
            #         #     continue 
            #         UrlQueue.append(GetMergeUrl(RootUrl, RootDomain, t))
            #         PathsPath[path].append(t)
            #         print(f"{Fore.RED}Find New Url! {Fore.YELLOW} Append visited url: {Fore.RED} {t} {Style.RESET_ALL}")
            #         VisitedUrl.append(t)
            #     # print(GetMergeUrl(RootUrl, RootDomain, t))
        elif tag.find("a"): # and tag.find("a").get("href") not in VisitedUrl and tag.find("a").get("href") != None:
            t = GetUrlPath(tag.find("a").get("href"), RootDomain)
            if t != None and t[0] != "#" :
                url = GetMergeUrl(path, t)
                if url not in VisitedUrl and url != None:
                    print(f"{Fore.RED}Find New Url! {Fore.YELLOW} Append visited url: {Fore.RED} {url} {Style.RESET_ALL}")
                    UrlQueue.append(url)
                    PathsPath[path].append(t)
                    VisitedUrl.append(url)
    #         if t != None and t[0] != "/" and t[0] != "#":
    #             t = GetUrlPath(path + t, RootDomain)
    #         if t not in VisitedUrl and t != None:
    #             if ("http" in t or "https" in t) and t != None and t != "" and t[0] != "#":
    #                 UrlQueue.append(GetMergeUrl(RootUrl, RootDomain, t))
    #                 PathsPath[path].append(t)
    #                 print(f"{Fore.RED}Find New Url! {Fore.YELLOW} Append visited url: {Fore.RED} {t} {Style.RESET_ALL}")
    #                 VisitedUrl.append(t)
    #                 # print(GetMergeUrl(RootUrl, RootDomain, t))
    #             elif "http" not in t and "https" not in t and t != None and t != "" and t[0] != "#":
    #                 # if(t[0] == "#") :
    #                 #     continue
    #                 UrlQueue.append(GetMergeUrl(RootUrl, RootDomain, t))
    #                 PathsPath[path].append(t)
    #                 print(f"{Fore.RED}Find New Url! {Fore.YELLOW} Append visited url: {Fore.RED} {t} {Style.RESET_ALL}")
    #                 VisitedUrl.append(t)
    #                 # print(GetMergeUrl(RootUrl, RootDomain, t))
    # # PrintUrlQueue(UrlQueue)
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
        driver, cookies = UrlInit(RootUrl, LoginUrl)
        # AllTags = GetAllTags(driver)
        RequestHandler = ApiSessionHandler(cookies)
        body_str = 'jform%5Btitle%5D=Getting+Started&jform%5Barticletext%5D=%3Cp%3EIt%27s+easy+to+get+started+creating+your+website.+Knowing+some+of+the+basics+will+help.%3C%2Fp%3E%0D%0A%3Ch3%3EWhat+is+a+Content+Management+System%3F%3C%2Fh3%3E%0D%0A%3Cp%3EA+content+management+system+is+software+that+allows+you+to+create+and+manage+webpages+easily+by+separating+the+creation+of+your+content+from+the+mechanics+required+to+present+it+on+the+web.%3C%2Fp%3E%0D%0A%3Cp%3EIn+this+site%2C+the+content+is+stored+in+a+%3Cem%3Edatabase%3C%2Fem%3E.+The+look+and+feel+are+created+by+a+%3Cem%3Etemplate%3C%2Fem%3E.+Joomla%21+brings+together+the+template+and+your+content+to+create+web+pages.%3C%2Fp%3E%0D%0A%3Ch3%3ELogging+in%3C%2Fh3%3E%0D%0A%3Cp%3ETo+login+to+your+site+use+the+user+name+and+password+that+were+created+as+part+of+the+installation+process.+Once+logged-in+you+will+be+able+to+create+and+edit+articles+and+modify+some+settings.%3C%2Fp%3E%0D%0A%3Ch3%3ECreating+an+article%3C%2Fh3%3E%0D%0A%3Cp%3EOnce+you+are+logged-in%2C+a+new+menu+will+be+visible.+To+create+a+new+article%2C+click+on+the+%22Submit+Article%22+link+on+that+menu.%3C%2Fp%3E%0D%0A%3Cp%3EThe+new+article+interface+gives+you+a+lot+of+options%2C+but+all+you+need+to+do+is+add+a+title+and+put+something+in+the+content+area.+To+make+it+easy+to+find%2C+set+the+state+to+published.%3C%2Fp%3E%0D%0A%3Cdiv%3EYou+can+edit+an+existing+article+by+clicking+on+the+edit+icon+%28this+only+displays+to+users+who+have+the+right+to+edit%29.%3C%2Fdiv%3E%0D%0A%3Ch3%3ETemplate%2C+site+settings%2C+and+modules%3C%2Fh3%3E%0D%0A%3Cp%3EThe+look+and+feel+of+your+site+is+controlled+by+a+template.+You+can+change+the+site+name%2C+background+colour%2C+highlights+colour+and+more+by+editing+the+template+settings.+Click+the+%22Template+Settings%22+in+the+user+menu.%3C%2Fp%3E%0D%0A%3Cp%3EThe+boxes+around+the+main+content+of+the+site+are+called+modules.+You+can+modify+modules+on+the+current+page+by+moving+your+cursor+to+the+module+and+clicking+the+edit+link.+Always+be+sure+to+save+and+close+any+module+you+edit.%3C%2Fp%3E%0D%0A%3Cp%3EYou+can+change+some+site+settings+such+as+the+site+name+and+description+by+clicking+on+the+%22Site+Settings%22+link.%3C%2Fp%3E%0D%0A%3Cp%3EMore+advanced+options+for+templates%2C+site+settings%2C+modules%2C+and+more+are+available+in+the+site+administrator.%3C%2Fp%3E%0D%0A%3Ch3%3ESite+and+Administrator%3C%2Fh3%3E%0D%0A%3Cp%3EYour+site+actually+has+two+separate+sites.+The+site+%28also+called+the+front+end%29+is+what+visitors+to+your+site+will+see.+The+administrator+%28also+called+the+back+end%29+is+only+used+by+people+managing+your+site.+You+can+access+the+administrator+by+clicking+the+%22Site+Administrator%22+link+on+the+%22User+Menu%22+menu+%28visible+once+you+login%29+or+by+adding+%2Fadministrator+to+the+end+of+your+domain+name.+The+same+user+name+and+password+are+used+for+both+sites.%3C%2Fp%3E%0D%0A%3Ch3%3ELearn+more%3C%2Fh3%3E%0D%0A%3Cp%3EThere+is+much+more+to+learn+about+how+to+use+Joomla%21+to+create+the+website+you+envision.+You+can+learn+much+more+at+the+%3Ca+href%3D%22https%3A%2F%2Fdocs.joomla.org%2F%22+target%3D%22_blank%22+rel%3D%22noopener+noreferrer%22%3EJoomla%21+documentation+site%3C%2Fa%3E+and+on+the%3Ca+href%3D%22https%3A%2F%2Fforum.joomla.org%2F%22+target%3D%22_blank%22+rel%3D%22noopener+noreferrer%22%3E+Joomla%21+forums%3C%2Fa%3E.%3C%2Fp%3E&jform%5Bcatid%5D=2&jform%5Btags%5D%5B%5D=2&jform%5Bnote%5D=&jform%5Bversion_note%5D=&jform%5Bcreated_by_alias%5D=&jform%5Bstate%5D=1&jform%5Bfeatured%5D=0&jform%5Bpublish_up%5D=2025-08-25+07%3A30%3A03&jform%5Bpublish_down%5D=&jform%5Baccess%5D=1&jform%5Blanguage%5D=*&jform%5Bmetadesc%5D=&jform%5Bmetakey%5D=&task=article.save&return=aHR0cDovLzE5Mi4xNjguMTEuMTI5OjgwODAv&c084e2511acf2a70d8ba6106c8bd8ea2=1'
        data = ParseBody(body_str)
        api_record = {
            'url': 'http://192.168.11.129:8080/index.php?a_id=1',
            'method': 'POST',
            'headers': {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'en-US,en;q=0.9',
                'Origin': 'http://192.168.11.129:8080',
                'Referer': 'http://192.168.11.129:8080/index.php/submit-an-article',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1'
            },
            'body': data
        }
        response = RequestHandler.SendApiRequest(api_record['method'], api_record['url'], api_record['headers'], api_record['body'])
        if response:
            print(f"{Fore.GREEN}API 請求成功！回傳內容: {response.text}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}API 請求失敗，請檢查日誌。{Style.RESET_ALL}")
        
        # GetNext(driver, RootUrl, RootUrl)
        # VisitedUrl.append(RootUrl)
        # i = 0
        # while len(UrlQueue)-1 > i :
        #     GetNext(driver, RootUrl, UrlQueue[i])
        #     i+=1
        #     print(f"{Fore.GREEN}Get Next Url: {Fore.RED} {UrlQueue[i]} {Style.RESET_ALL}")
        # print(f"{Fore.GREEN}Done{Style.RESET_ALL}")
        # for i in range(len(VisitedUrl)):
        #     print(VisitedUrl[i])
        
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
    finally:
        if driver:
            driver.close()
            print(f"{Fore.GREEN}Driver closed.{Style.RESET_ALL}")
        # if MitmProcess:
        #     StopMitmProxy(MitmProcess)

    
    # with open("PathsApi.txt", "w") as f:
    #     for path in PathsApi:
    #         f.write(f"{path}{Style.RESET_ALL}\n")
    #         f.write(f" -> {PathsApi[path]}{Style.RESET_ALL}\n")
    #         # print(f"{Fore.BLUE}[*]{path}{Style.RESET_ALL}")
    #         # print(f"{Fore.RED}{PathsApi[path]}{Style.RESET_ALL}")
    # with open("PathsPath.txt", "w") as f:
    #     # print("\n\nPathspath:")
    #     for path in PathsPath:
    #         f.write(f"{path}{Style.RESET_ALL}\n")
    #         f.write(f" -> {PathsPath[path]}{Style.RESET_ALL}\n")
    #         # print(f"{Fore.BLUE}[*]{path}{Style.RESET_ALL}")
    #         # print(f"{Fore.RED}{PathsPath[path]}{Style.RESET_ALL}")
    

if __name__ == "__main__":
    RootUrl = "http://192.168.11.129:8080/index.php"
    LoginUrl = "http://192.168.11.129:8080/administrator"
    # print(GetDomainName("https://www.joomla.org"))
    init(autoreset=True)
    main(RootUrl, LoginUrl)
    