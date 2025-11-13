from seleniumwire import webdriver
import requests
from bs4 import BeautifulSoup, Tag, NavigableString
from colorama import Fore, Style, init
import os, sys
import json
from collections import deque
import re
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from modules.requests_handler import ApiSessionHandler
from Fuzzing.Fuzzer import generatePayload
init(autoreset=True)

ResourcesPool = "../ResourcesPool/"
regexPattern = r"MTSEC-[a-f0-9]{12}-F\d+"
reflectMap = {}
hashApiMap = {}
hashSet = set()
def GetPath() :
    with open(ResourcesPool + "tree.json", "r") as f:
        return json.load(f)

def GetLoginSession():
    with open(ResourcesPool + "LoginSession.json", "r", encoding="utf-8") as f:
        return json.load(f)

def LoginCheck(LoginSession):
    RequestHandler = ApiSessionHandler(LoginSession["Cookies"])
    res = RequestHandler.SendApiRequest("get", "http://192.168.11.129:8080/administrator/", None, None)
    if len(res.text) > 30000:
        print(f"{Fore.GREEN}Login Success{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Login Failed{Style.RESET_ALL}")

def FindString(response, regexPattern):
    if response is None:
        return None
    soup = BeautifulSoup(response.text, "html.parser")
    reflect = {}
    
    def addToReflect(tag, location):
        if tag not in reflect:
            reflect[tag] = []
        reflect[tag].append(location)
        h, arg = parseIstring(tag)
        hashSet.add(h)

    for tag in soup.find_all(True):
        for attr, value in tag.attrs.items():
            if type(value) == str:
                matches = re.findall(regexPattern, value)
                for tag_name in matches:
                    location = f"{tag.name}[{attr}]"
                    addToReflect(tag_name, location)
            if tag.string and isinstance(tag.string, NavigableString):
                matches = re.findall(regexPattern, tag.string)
                for tag_name in matches:
                    location = f"{tag.name}::text"
                    addToReflect(tag_name, location)

    # matches = re.findall(regexPattern, response.text)
    return reflect

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

def parseIstring(istr):
    istr = istr.split("-")
    istr[2] = int(istr[2][1:])
    istr.pop(0)
    return istr

def findBodyKeyNameByIndex(body, index):
    for i, (key, value) in enumerate(body.items()):
        if i == index:
            return key, value

if __name__ == "__main__" :
    # for i in range(5):
    #     print(generatePayload())
    #     print("")
    LoginCheck(GetLoginSession())
    LoginSession = GetLoginSession()
    requestHandler = ApiSessionHandler(LoginSession["Cookies"])
    tree = GetPath()
    allUrls = BFS(tree)
    count = 0
    for url in allUrls:
        print(f"\n{Fore.CYAN}STARTING URL: {url}{Style.RESET_ALL}")
        res = requestHandler.SendApiRequest("get", url, None, None)
        result = FindString(res, regexPattern)
        if result:
            if url not in reflectMap:
                reflectMap[url] = {}
            for tag, locations in result.items():
                reflectMap[url] = result
            count += 1
        else:
            print(f"{Fore.RED}No result found{Style.RESET_ALL}")

    for url, result in reflectMap.items():
       print(url)
       print(result)
       print("--------------------------------")

    print(f"{Fore.GREEN}Total result found: {count}{Style.RESET_ALL}")
    

    with open(ResourcesPool + "reflectMap.json", "w", encoding="utf-8") as f:
        json.dump(reflectMap, f, ensure_ascii=False, indent=4)

    print(hashSet)

    # --------------------------

    # with open(ResourcesPool + "reflectMap.json", "r", encoding="utf-8") as f:
    #     reflectMap = json.load(f)

    # apis = {}
    # with open(ResourcesPool + "Apis.json", "r", encoding="utf-8") as f:
    #     apis = json.load(f)

    hashes = {}
    with open(ResourcesPool + "hashToApi.json", "r", encoding="utf-8") as f:
        hashes = json.load(f)

    for k in list(hashes.keys()):
        if k not in hashSet:
            del hashes[k]

    with open(ResourcesPool + "hashToApi.json", "w", encoding="utf-8") as f:
        json.dump(hashes, f, ensure_ascii=False, indent=4)

    # for k, v in hashes.items():
    #     data = hashes[k]['body']
    #     temp = data
    #     flag = True
    #     while flag:
    #         for i in data:
    #             if data[i] == "Fuzzable":
    #                 temp[i] = generatePayload()
    #         response = requestHandler.SendApiRequest(hashes[k]['method'].upper(), hashes[k]['url'], hashes[k]['headers'], temp)
    #         if response.status_code >= 200 and response.status_code < 300:
    #             flag = False

    # for url, result in reflectMap.items():
    #     for tag in result.keys():
    #         h, arg = parseIstring(tag)
    #         if h not in hashApiMap:
    #             hashApiMap[h] = hashes[h]
    #         for i in range(arg+1):
    #             if
    #         # hashApiMap[h]['reflectUrl'] = url
    #         # print(apis[url])
    #         # print(url)

    #         for k in apis[url]:
    #             print(k)
    #             if apis[url][k].get('hash12') == h: 
    #                 hashApiMap[h]['apiUrl'] = k
    #                 hashApiMap[h]['body'] = k['body']
    #                 hashApiMap[h]['hash40'] = k['hash40']

    # print(hashApiMap)
    # with open(ResourcesPool + "hashApiMap.json", "w", encoding="utf-8") as f:
    #     json.dump(hashApiMap, f, ensure_ascii=False, indent=4)
            
        