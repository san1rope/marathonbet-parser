import asyncio
import os

from aiohttp import BasicAuth
from undetected_chromedriver import ChromeOptions, Chrome

from config import Config
from models import Proxy


async def main():
    proxy = Proxy(host="s-22494.sp6.ovh", port=11010, username="V4zH2d_9", password=hhNUPsJfpskT)
    cookie = ""

    proxy_ip = f"http://{proxy.host}:{proxy.port}"
    proxy_auth = BasicAuth(login=proxy.username, password=proxy.password)
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
        "cookie": f"cf_clearance={cookie}",
        "priority": "u=0, i",
        "referer": "https://www.marathonbet.com/su/?cppcids=all",
        "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Opera GX";v="117"',
        "sec-ch-ua-mobile": '?0',
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": 'document',
        "sec-fetch-mode": 'navigate',
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": Config.USER_AGENT
    }


if __name__ == "__main__":
    asyncio.run(main())
