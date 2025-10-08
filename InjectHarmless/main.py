import os, sys
import json
from colorama import Fore, Style, init
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import requests
from modules.requests_handler import ApiSessionHandler
from modules.ParseArg import ParseBody
from modules.AnalyseInput import BuildData

ResourcesPool = "../ResourcesPool/"
ExcludeKeywords = []

def GetLoginSession():
    with open(ResourcesPool + "LoginSession.json", "r", encoding="utf-8") as f:
        return json.load(f)

def GetApis():
    apis = open(ResourcesPool + "apis.json", "r", encoding="utf-8").read()
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
    for key in Apis.keys():
        for key_ in Apis[key].keys():
            if Apis[key][key_] != {}:
                Headers = Apis[key][key_]["headers"]
                Body = Apis[key][key_]["body"]
                if type(Body) == dict:
                    for k in Body.keys() :
                        if Body[k] == "Fuzzable":
                            FuzzableCount += 1
                            Body[k] += str(FuzzableCount)
                response = RequestHandler.SendApiRequest(Apis[key][key_]["method"], key, Headers, Body)
                if response:
                    print(f"{Fore.GREEN}API 請求成功！回傳內容: {response.status_code}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}API 請求失敗，請檢查日誌。{Style.RESET_ALL}")
    # 目前這邊可以自動執行 requests，並且可以順利修改到網頁內容
    # 例如把 Fuzzable 改成 aaa1234 後可以在網頁上的文章中確實看到真的有一篇 aaa1234 的文章
    # 可以用更多筆的測試資料來測試 然後就要確認一下要如何注入高辨識度的資料

    # print(response.text)
    # AddExcludeKeywords(["login", "logout", "install", "installer", "plugin"])
    # print(GetExcludeKeywords())
    # for key in Apis.keys():
    #     if Apis[key] != {}:
    #         for key_ in Apis[key].keys():
    #             api = {
    #                 "url": key_,
    #                 "method": Apis[key][key_]["method"],
    #                 "headers": Apis[key][key_]["headers"],
    #                 "body": Apis[key][key_]["body"]
    #             }
    #             response = RequestHandler.SendApiRequest(api["method"], api["url"], LoginSession["Headers"], api["body"])
    #             if response:
    #                 print(f"{Fore.GREEN}API 請求成功！回傳內容: {response.status_code}{Style.RESET_ALL}")
    #             else:
    #                 print(f"{Fore.RED}API 請求失敗，請檢查日誌。{Style.RESET_ALL}")


"""
    Headers = {
        "Host": "192.168.11.129:8080",
        "Proxy-Connection": "keep-alive",
        "Content-Length": "3751",
        "Cache-Control": "max-age=0",
        "Origin": "http://192.168.11.129:8080",
        "Content-Type": "application/x-www-form-urlencoded",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Referer": "http://192.168.11.129:8080/index.php?view=form&layout=edit&a_id=1&return=aHR0cDovLzE5Mi4xNjguMTEuMTI5OjgwODAvaW5kZXgucGhw",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cookie": "1cb674bfbaa9285a64bd5f249c97c3da=9b14df3b42d9b4bcb67903a3e9aa3263; joomla_user_state=logged_in; 0a9483a6415b9eafd7217d9a24a88aa8=c65419f15fe06e7112b78c429fc9d36d"
      }
    api = {
        "url": "http://192.168.11.129:8080/index.php?a_id=1",
        "method": "post",
        "headers": Headers,
        "body": {
            "jform[title]": "bbb123456",
            "jform[articletext]": "<p>It's easy to get started creating your website. Knowing some of the basics will help.</p>\r\n<h3>What is a Content Management System?</h3>\r\n<p>A content management system is software that allows you to create and manage webpages easily by separating the creation of your content from the mechanics required to present it on the web.</p>\r\n<p>In this site, the content is stored in a <em>database</em>. The look and feel are created by a <em>template</em>. Joomla! brings together the template and your content to create web pages.</p>\r\n<h3>Logging in</h3>\r\n<p>To login to your site use the user name and password that were created as part of the installation process. Once logged-in you will be able to create and edit articles and modify some settings.</p>\r\n<h3>Creating an article</h3>\r\n<p>Once you are logged-in, a new menu will be visible. To create a new article, click on the \"Submit Article\" link on that menu.</p>\r\n<p>The new article interface gives you a lot of options, but all you need to do is add a title and put something in the content area. To make it easy to find, set the state to published.</p>\r\n<div>You can edit an existing article by clicking on the edit icon (this only displays to users who have the right to edit).</div>\r\n<h3>Template, site settings, and modules</h3>\r\n<p>The look and feel of your site is controlled by a template. You can change the site name, background colour, highlights colour and more by editing the template settings. Click the \"Template Settings\" in the user menu.</p>\r\n<p>The boxes around the main content of the site are called modules. You can modify modules on the current page by moving your cursor to the module and clicking the edit link. Always be sure to save and close any module you edit.</p>\r\n<p>You can change some site settings such as the site name and description by clicking on the \"Site Settings\" link.</p>\r\n<p>More advanced options for templates, site settings, modules, and more are available in the site administrator.</p>\r\n<h3>Site and Administrator</h3>\r\n<p>Your site actually has two separate sites. The site (also called the front end) is what visitors to your site will see. The administrator (also called the back end) is only used by people managing your site. You can access the administrator by clicking the \"Site Administrator\" link on the \"User Menu\" menu (visible once you login) or by adding /administrator to the end of your domain name. The same user name and password are used for both sites.</p>\r\n<h3>Learn more</h3>\r\n<p>There is much more to learn about how to use Joomla! to create the website you envision. You can learn much more at the <a href=\"https://docs.joomla.org/\" target=\"_blank\" rel=\"noopener noreferrer\">Joomla! documentation site</a> and on the<a href=\"https://forum.joomla.org/\" target=\"_blank\" rel=\"noopener noreferrer\"> Joomla! forums</a>.</p>",
            "jform[catid]": "2",
            "jform[tags][]": "2",
            "jform[note]": "",
            "jform[version_note]": "",
            "jform[created_by_alias]": "",
            "jform[state]": "1",
            "jform[featured]": "0",
            "jform[publish_up]": "2025-10-07 01:38:20",
            "jform[publish_down]": "",
            "jform[access]": "1",
            "jform[language]": "*",
            "jform[metadesc]": "",
            "jform[metakey]": "",
            "task": "article.save",
            "return": "aHR0cDovLzE5Mi4xNjguMTEuMTI5OjgwODAvaW5kZXgucGhw",
            "eea3fbd08df9050f54bae1d3bc9083a2": "1"
      },
    }
    response = RequestHandler.SendApiRequest(api["method"], api["url"], api["headers"], api["body"])
"""