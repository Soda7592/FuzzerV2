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

UrlQueue = []
VisitedUrl = []

def UrlInit(RootUrl):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(RootUrl)
        VisitedUrl.append(GetUrlPath(RootUrl, GetDomainName(RootUrl)))
        FullHTML = driver.page_source
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
    GetStaticUrl(AllTags, url)

def main(RootUrl):
    driver = UrlInit(RootUrl)
    AllTags = GetAllTags(driver)
    UrlQueue = GetStaticUrl(AllTags, RootUrl)
    # GetNext(driver, UrlQueue[3])
    for i in range(len(UrlQueue)):
        GetNext(driver, UrlQueue[i])
    print(f"{Fore.GREEN}Done{Style.RESET_ALL}")
    for i in range(len(VisitedUrl)):
        print(VisitedUrl[i])
    

# def TestDriver(driver, RootUrl): 
#     driver.get("http://192.168.11.129:8080/index.php/your-profile")
#     time.sleep(2)
#     FullHTML = driver.page_source
#     soup = BeautifulSoup(FullHTML, "html.parser")
#     AllTags = soup.find_all()
#     form = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "member-profile")))
#     filedset = form.find_elements(By.TAG_NAME, "fieldset")
#     for fieldset in filedset:
#         print(fieldset.text)

if __name__ == "__main__":
    RootUrl = "http://192.168.11.129:8080/index.php"
    # print(GetDomainName("https://www.joomla.org"))
    init(autoreset=True)
    main(RootUrl)
    
