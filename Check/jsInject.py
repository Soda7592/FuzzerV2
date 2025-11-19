from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

override_script = """
(function() {
    window.__xss_markers = [];
    if (window === window.top) {
        window.addEventListener('message', function(event) {
            if (event.data && event.data.type === 'XSS_REPORT') {
                window.__xss_markers.push(event.data.msg);
            }
        });
    }

    const originalAlert = window.alert;
    window.alert = function(message) {
        const msg = String(message || '');
        
        console.log('[CUSTOM ALERT context: ' + window.location.href + '] ' + msg);
        
        if (window === window.top) {
            window.__xss_markers.push(msg);
        } else {
            window.top.postMessage({type: 'XSS_REPORT', msg: msg}, '*');
        }
    };

    window.getXssMarkers = function() {
        return window.__xss_markers;
    };
})();
"""

driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": override_script
})

driver.get("http://localhost:5500/Check/test.html")
import time
time.sleep(3)
alert_messages = driver.execute_script("return window.getXssMarkers() || [];")

print("所有觸發的 alert 內容：", alert_messages)
MY_MARKER = "testalert"

for msg in alert_messages:
    if MY_MARKER in msg:
        print(f"XSS 確認！漏洞證據：{msg}")
        break
else:
    print("沒有觸發我們的 payload（可能是正常 alert）")

input()