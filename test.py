import asyncio
import logging
import os

from aiohttp import BasicAuth, ClientSession
from bs4 import BeautifulSoup
from undetected_chromedriver import ChromeOptions, Chrome

from config import Config
from models import Proxy
from utils import Utils as Ut

logger = logging.getLogger(__name__)


async def main():
    proxy = Proxy(host="s-22494.sp6.ovh", port=11001, username="V4zH2d_0", password="hhNUPsJfpskT")
    # print(await Ut.verify_browser(proxy=proxy))
    # return
    cookie = "EFEX7s.5J0kxWIxCDSuh7e3yRAn7JzOtTCjBnPHQIgI-1743396549-1.2.1.1-n9rnxnYhpoRCDxVadfZV8PVm6hMt.pYZw.ZUZfSgwOgpqZP.bLr92UzrnfrWDu3hmPilNdC8E8EyRvn5ht2PTamSX3mVTSXcV51RQ8Tc2svn3wkiWO7xxguqQv.cbllDn2_3RKvPeAKOSz_H.SvFhjPLrNsD0kP9p91XqSqTIveIcBVV6VCKOIlq9lA8N2kxap0ul3Xxf4IZWPmsEakYumrrxO9LMoD2qLaJGaKw7hVPvzIlZvf6u1kFKi18CVXM1PqVU9tHumDTZS5cN13eKkN98_Gd9nFo0uRoqFc1s.gU__4vl_87Pu3Rsbp1VWkMss70E3QYMi2PyGnvS71OWg3sQq3YcSQnfLWY5sClTIIHurp55f71rXlJuDq4yJoIjSISg69Bc0J0dlZbS2s6.wSygPfhY81_lDG3zWw6J74"

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

    request_default_kwargs = {"headers": headers, "proxy": proxy_ip, "proxy_auth": proxy_auth, "timeout": 20}
    async with ClientSession() as session:
        page_url = f"https://www.marathonbet.com/en/live/"
        async with session.get(url=page_url, **request_default_kwargs) as response:
            page_markup = await response.text()
            soup_page = BeautifulSoup(page_markup, "lxml")

        category_els = soup_page.find("div", {"data-id": "container_EVENTS"}).find(
            "div", {"class": "sport-category-container", "data-sport-treeid": "22723"}).find(
            "div", {"class": "sport-category-content"})
        event_pages_urls = category_els.find_all("a", {"class": "category-label-link"})
        for event_page_url_el in event_pages_urls:
            event_page_url = "https://www.marathonbet.com" + event_page_url_el["href"]
            print(f"event_page_url = {event_page_url}")
            async with session.get(url=event_page_url, **request_default_kwargs) as response:
                event_page_markup = await response.text()
                # with open("league.html", "w", encoding="utf-8") as file:
                #     print("uploaded")
                #     file.write(event_page_markup)

                soup_event_page = BeautifulSoup(event_page_markup, "lxml")

            events_elements = soup_event_page.find_all("div", class_="coupon-row")
            if len(events_elements) == 1:
                out_data = await Ut().parse_data_from_event_football(soup=soup_event_page)
                print(out_data)  # in progres...
                continue

            for event_el in events_elements:
                event_url = f"https://www.marathonbet.com/en/live/{event_el['data-event-treeid']}"
                print(f"event_url = {event_url}")
                async with session.get(url=event_url, **request_default_kwargs) as response:
                    event_markup = await response.text()
                    # with open("event_2.html", "w", encoding="utf-8") as file:
                    #     file.write(event_markup)

                    soup_event = BeautifulSoup(event_markup, "lxml")

                out_data = await Ut().parse_data_from_event_tennis(soup=soup_event)
                print(out_data)


async def main2():
    options = ChromeOptions()
    options.add_argument(f"--user-agent={Config.USER_AGENT}")
    options.add_argument(f'--load-extension={os.getcwd()}/s-22494.sp6.ovh_11001_V4zH2d_0_hhNUPsJfpskT/')
    options.add_argument("--disable-blink-features=AutomationControlled")

    with Chrome(options=options) as driver:
        driver.get("https://www.marathonbet.com/su/live/popular")

        await asyncio.sleep(2000)


if __name__ == "__main__":
    asyncio.run(main2())
