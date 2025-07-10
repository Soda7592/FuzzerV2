from mitmproxy import http
import json
import asyncio
import collections 
from colorama import Fore, Back, Style, init
from aiohttp import web

init(autoreset=True)
CollectedApiRequests = collections.deque()
WebApiPort = 8081

async def WebHandleRequest(request):
    data = []
    while CollectedApiRequests:
        data.append(CollectedApiRequests.popleft())
    print(f"{Fore.GREEN}[*] Addon Web API: Sending {len(data)} captured requests to client.{Style.RESET_ALL}")

    return web.json_response(data)

async def RunWebApi():
    app = web.Application()
    app.router.add_get("/api/requests", WebHandleRequest)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", WebApiPort)
    await site.start()
    print(f"{Fore.GREEN}[*] Addon Web API: Running on http://127.0.0.1:{WebApiPort}{Style.RESET_ALL}")
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        await runner.cleanup()
        print(f"{Fore.RED}[*] Addon Web API: Task cancelled.{Style.RESET_ALL}")
    finally:
        await runner.cleanup()
        print(f"{Fore.RED}[*] Addon Web API: Task stopped.{Style.RESET_ALL}")


class APICollector:
    def __init__(self):
        self.WebApiTask = None
        self.TargetDomain = "192.168.11.129"

        self.StaticExtensions = (
            '.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', 
            '.woff', '.woff2', '.ttf', '.eot', '.map',
            '.webp', '.mp4', '.webm', '.ogg', '.mp3', '.wav',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.zip', '.rar', '.tar.gz',
        )

        self.StaticPathPrefixes = (
            '/static/', '/assets/', '/images/', '/fonts/', '/media/', '/css/', '/js/', '/img/', '/icon/', '/favicon/',
            '/fonts/', '/media/', '/css/', '/js/', '/img/', '/icon/', '/favicon/',
        )
        
    async def running(self):
        if self.WebApiTask is None:
            self.WebApiTask = asyncio.create_task(RunWebApi())
            print(f"{Fore.GREEN}[*] Addon Web API: Task started.{Style.RESET_ALL}")

    def request(self, flow: http.HTTPFlow):
        """當接收到新的 HTTP 請求時觸發"""
        if "googleapis.com" in flow.request.host \
        or "google.com" in flow.request.host \
        or "gstatic.com" in flow.request.host \
        or "optimizationguide-pa.googleapis.com" in flow.request.host :
            return
        if self.TargetDomain != flow.request.host:
            print(f"{Fore.WHITE}[*] Addon Web API: Skipping request to {flow.request.host}{Style.RESET_ALL}")
            return 
        
        UrlPath = flow.request.path.lower()
        if any(UrlPath.startswith(prefix) for prefix in self.StaticPathPrefixes):
            print(f"{Fore.WHITE}[*] Addon Web API: Skipping static file request: {flow.request.pretty_url}{Style.RESET_ALL}")
            return
        if any(UrlPath.endswith(ext) for ext in self.StaticExtensions):
            print(f"{Fore.WHITE}[*] Addon Web API: Skipping static file request: {flow.request.pretty_url}{Style.RESET_ALL}")
            return

        try:
            RequestBody = None
            if flow.request.content:
                try:
                    RequestBody = flow.request.content.decode('utf-8')
                except UnicodeDecodeError:
                    RequestBody = f"Binary content ({len(flow.request.content)} bytes)"
                except json.JSONDecodeError:
                    pass

            data = ({
                "url": flow.request.pretty_url,
                "method": flow.request.method,
                "headers": dict(flow.request.headers),
                "body": RequestBody,
                "timestamp": flow.request.timestamp_start
            })
            CollectedApiRequests.append(data)
            print(f"{Fore.MAGENTA}[*] Addon Captured Target Domain Request: {flow.request.method} {flow.request.pretty_url}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[*] Addon Web API: Error: {e}{Style.RESET_ALL}")

    def response(self, flow: http.HTTPFlow): 
        pass

    def done(self):
        if self.WebApiTask:
            self.WebApiTask.cancel()
            self.WebApiTask = None
        print(f"{Fore.RED}[*] Addon Web API: Task stopped.{Style.RESET_ALL}")

addons = [
    APICollector()
]
