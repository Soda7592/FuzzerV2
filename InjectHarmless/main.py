import os, sys
import json
from colorama import Fore, Style, init
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import requests
from modules.requests_handler import ApiSessionHandler
from modules.ParseArg import ParseBody
from modules.AnalyseInput import BuildData
from hashlib import sha1

ResourcesPool = "../ResourcesPool/"
ExcludeKeywords = []

def GetLoginSession():
    with open(ResourcesPool + "LoginSession.json", "r", encoding="utf-8") as f:
        return json.load(f)

def GetApis():
    apis = open(ResourcesPool + "Apis.json", "r", encoding="utf-8").read()
    return json.loads(apis)

def GetUrlInfo(url):
    with open(ResourcesPool + "tree.json", "r", encoding="utf-8") as f:
        return json.load(f)

def AddExcludeKeywords(urls):
    ExcludeKeywords.extend(urls)

def GetExcludeKeywords():
    return ExcludeKeywords

def LoginCheck(LoginSession):
    RequestHandler = ApiSessionHandler(LoginSession["Cookies"])
    res = RequestHandler.SendApiRequest("get", "http://192.168.11.129:8080/administrator/", None, None)
    if len(res.text) > 30000:
        print(f"{Fore.GREEN}Login Success{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Login Failed{Style.RESET_ALL}")

if __name__ == "__main__":
    init(autoreset=True)
    LoginCheck(GetLoginSession())
    LoginSession = GetLoginSession()
    # print(LoginSession["Headers"])
    RequestHandler = ApiSessionHandler(LoginSession["Cookies"])
    FuzzableCount = 1
    Apis = GetApis()
    # print(Apis)
    for key in Apis.keys():
        for key_ in Apis[key].keys():
            if Apis[key][key_] != {}:
                Headers = Apis[key][key_]["headers"]
                Body = Apis[key][key_]["body"]
                if type(Body) == dict:
                    count = 0
                    for k in Body.keys() :
                        if Body[k] == "Fuzzable":
                            print(key_)
                            sha1_hash = str(sha1(key_.encode('utf-8')).hexdigest())[:12]
                            print(sha1_hash)
                            Body[k] = "MTSEC-" + sha1_hash + "-" + str("F" + str(count))
                            count += 1
                            # print(Body[k])
                response = RequestHandler.SendApiRequest(Apis[key][key_]["method"].upper(), key, Headers, Body)
                if response:
                    print(f"{Fore.GREEN}API 請求成功！回傳內容: {response.status_code}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}API 請求失敗，請檢查日誌。{Style.RESET_ALL}")