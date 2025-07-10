# Install

1. `pip install mitmproxy aiohttp`

2. `.mitmproxy` directory will be generated in your user directory, put certificate into browser if your need intercept encryptioned traffic.

3. Start your mitmproxy server by using command `mitmdump -p 8080 -s api_collector_addon.py --ssl-insecure --quiet`

4. Then you can start crawler.
