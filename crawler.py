from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


def UrlInit(RootUrl):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(RootUrl)
        time.sleep(2)
        username = driver.find_element(By.ID, "modlgn-username")
        password = driver.find_element(By.ID, "modlgn-passwd")
        username.send_keys("user")
        password.send_keys("password")
        button = driver.find_element(By.NAME, "Submit")
        button.click()
        time.sleep(2)
        return driver
    except Exception as e:
        print(f"Error: {e}")

def AllTags(driver):
    try:
        FullHTML = driver.page_source
        soup = BeautifulSoup(FullHTML, "html.parser")
        all_tags = soup.find_all()
        return all_tags
    except Exception as e:
        print(f"Error: {e}")
    

def DivideDomain(url) :
    if "http" in url or "https" in url:
        start = url.find("//")
        end = url.find("/", start + 2) # Find slash and start from start+2 index.
        return url[start + 2:end]
    else:
        return url


def GetStaticUrl(AllTags, RootUrl):
    UrlQueue = []
    RootDomain = DivideDomain(RootUrl)
    for tag in AllTags:
        if tag.name == "a" and tag.get("href") not in UrlQueue and tag.get("href") != None:
            div = DivideDomain(tag.get("href"))
            t = tag.get("href")
            if ("http" in t or "https" in t) and div == RootDomain and t != None:
                UrlQueue.append(t)
            elif "http" not in t and "https" not in t and t != None and t != "":
                if(t[0] == "#") :
                    continue 
                UrlQueue.append(t)
        elif tag.find("a") and tag.find("a").get("href") not in UrlQueue and tag.find("a").get("href") != None:
            div = DivideDomain(tag.find("a").get("href"))
            t = tag.find("a").get("href")
            if ("http" in t or "https" in t) and div == RootDomain and t != None:
                UrlQueue.append(t)
            elif "http" not in t and "https" not in t and t != None:
                if(t[0] == "#") :
                    continue
                UrlQueue.append(t)
    return UrlQueue

def main(RootUrl):
    driver = UrlInit(RootUrl)
    all_tags = AllTags(driver)
    UrlQueue = GetStaticUrl(all_tags, RootUrl)
    for url in UrlQueue:
        print(url)

if __name__ == "__main__":
    RootUrl = "http://192.168.11.129:8080/index.php"
    main()
