import logging
import os
import re
import asyncio
import multiprocessing
import traceback
from typing import List, Union, Any

from bs4 import BeautifulSoup
from undetected_chromedriver import ChromeOptions, Chrome

from config import Config
from models import Proxy

logger = logging.getLogger(__name__)


class Utils:

    @staticmethod
    def wrapper(func, *args, **kwargs) -> Any:
        return asyncio.run(func(*args, **kwargs))

    @staticmethod
    async def get_proxy_obj(proxy: str) -> Proxy:
        host, port, username, password = proxy.split(":")
        return Proxy(host=host, port=port, username=username, password=password)

    @staticmethod
    async def load_proxy_from_file(filepath: str = os.path.abspath("proxies.txt")) -> List[Proxy]:
        with open(filepath, "r", encoding="utf-8") as file:
            proxies_list_str = file.read().split("\n")

        proxies_list_obj = []
        for proxy_str in proxies_list_str:
            proxy_obj: Proxy = await Proxy.get_proxy_obj(proxy=proxy_str)
            proxies_list_obj.append(proxy_obj)
            await proxy_obj.create_proxy_extension()

        return proxies_list_obj

    @staticmethod
    async def verify_browser(proxy: Proxy, retries: int = 3) -> Union[List, bool]:
        current_process = multiprocessing.current_process().name == 'MainProcess'
        if not current_process:
            logging.basicConfig(
                level=logging.INFO,
                format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s')

        proxy_filename = await proxy.formulate_filename()

        options = ChromeOptions()
        options.add_argument(f"--user-agent={Config.USER_AGENT}")
        options.add_argument(f'--load-extension={os.getcwd()}/proxy-extensions/{proxy_filename}/')
        if Config.HEADLESS:
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")

        try:
            driver = Chrome(options=options)

        except FileExistsError:
            print(traceback.format_exc())
            return False

        driver.get("https://marathonbet.com/su/betting/Football+-+11")
        await asyncio.sleep(30)

        cookies = driver.get_cookies()
        for cookie in cookies:
            if cookie.get("name") == "cf_clearance":
                logger.info(f"Прошел проверку на браузер! {proxy}")
                driver.quit()
                return [proxy, cookie.get("value")]

        if retries:
            logger.warning(f"Не прошел браузерную проверку! {proxy} Осталось попыток: {retries}")
            driver.quit()
            return await Utils.verify_browser(proxy=proxy, retries=retries - 1)

        else:
            driver.quit()
            return False

    @staticmethod
    async def get_table_values(soup_obj: BeautifulSoup, class_main: str):
        totals_list = soup_obj.find("div", {"data-preference-id": re.compile(class_main)}).find_all(
            "tr", {"data-mutable-id": re.compile("MG")})
        totals_values = {}
        flag = False
        for total_pair in totals_list[1:]:
            te = total_pair.find_all(class_=re.compile("coeff-link-2way"))
            if len(te) == 0:
                if flag:
                    odd_and_even_values = total_pair.find_all("span")
                    odd_value = odd_and_even_values[0].text.strip()
                    even_value = odd_and_even_values[1].text.strip()
                    totals_values.update({
                        totals_list.index(total_pair): {"odd": odd_value, "even": even_value}
                    })

                else:
                    odd_el = total_pair.find("th", {"data-mutable-id": re.compile("ODD_Total_Goals")})
                    if odd_el:
                        flag = True

                continue

            coeff_less_value = te[0].find(class_="coeff-value").text.strip()
            coeff_less_price = te[0].find(class_="coeff-price").text.strip()
            coeff_more_value = te[1].find(class_="coeff-value").text.strip()
            coeff_more_price = te[1].find(class_="coeff-price").text.strip()
            totals_values.update({
                totals_list.index(total_pair): {
                    "less": coeff_less_value + " " + coeff_less_price,
                    "more": coeff_more_value + " " + coeff_more_price
                }
            })

        return totals_values
