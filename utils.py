import logging
import os
import re
import asyncio
import multiprocessing
import time
import traceback
from typing import List, Union, Any, Optional

from bs4 import BeautifulSoup, PageElement
from selenium.common import WebDriverException
from undetected_chromedriver import ChromeOptions, Chrome
from urllib3.exceptions import ReadTimeoutError
from webdriver_manager.chrome import ChromeDriverManager

from config import Config, PROXIES
from models import Proxy

logger = logging.getLogger(__name__)
current_proxy_index: Optional[int] = None


class Utils:
    FOOTBALL = "football"
    TENNIS = "tennis"

    @staticmethod
    def wrapper(func, *args, **kwargs) -> Any:
        return asyncio.run(func(*args, **kwargs))

    @staticmethod
    async def worker(semaphore, func, **kwargs):
        async with semaphore:
            return await func(**kwargs)

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
    async def get_next_proxy(current_proxy_index: int):
        if current_proxy_index is None:
            current_proxy_index = 0

        else:
            current_proxy_index += 1

        proxy, cookie = PROXIES[current_proxy_index]
        current_proxy_index += 1
        return [proxy, cookie]

    @staticmethod
    async def verify_browser(proxy: Proxy, retries: int = 3) -> Union[List, bool]:
        logger.info(f"{proxy} | Start verify...")

        current_process = multiprocessing.current_process().name == 'MainProcess'
        if not current_process:
            logging.basicConfig(
                level=logging.INFO,
                format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s')

        proxy_filename = await proxy.formulate_filename()

        options = ChromeOptions()
        options.add_argument(f"--user-agent={Config.USER_AGENT}")

        if proxy.username is None:
            options.add_argument(f"--proxy-server={proxy.host}:{proxy.port}")

        else:
            options.add_argument(f'--load-extension={os.getcwd()}/proxy-extensions/{proxy_filename}/')

        if Config.HEADLESS:
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")

        try:
            driver = Chrome(options=options, use_subprocess=True,
                            driver_executable_path=ChromeDriverManager().install())

        except FileExistsError:
            print(traceback.format_exc())
            return False

        try:
            driver.get("https://marathonbet.com/su/betting/Football")

        except (WebDriverException, ReadTimeoutError):
            return False

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
        try:
            totals_list = soup_obj.find("div", {"data-preference-id": re.compile(class_main)}).find_all(
                "tr", {"data-mutable-id": re.compile("MG")})

        except AttributeError:
            return None

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

    @staticmethod
    async def extract_odds_data(soup_el, data_market_type):
        result = {}
        try:
            odds_elements = await soup_el.find("td", {"data-market-type": data_market_type})
            for odds_element in odds_elements:
                label_element = odds_element.find(class_="left-simple")
                label = label_element.text.strip() if label_element else ""

                middle_element = await odds_element.find(class_="middle-simple")
                middle = middle_element.text.strip() if middle_element else ""

                value_element = await odds_element.find(class_="selection-link")
                value = value_element.text.strip() if value_element else ""

                if middle:
                    key = f"{label.strip()} {middle.strip()}"
                else:
                    key = label.strip()

                if key and value:
                    result[key] = value.strip()

        except Exception:
            print(traceback.format_exc())
            logger.warning(f"Не смог получить кф по {data_market_type}")

        return result

    @classmethod
    async def parse_data_from_event_football(cls, soup: [BeautifulSoup, PageElement]):
        match_data = {}

        try:
            event_id = soup.find(class_=re.compile("coupon-row")).get("data-event-eventid")
            if not event_id:
                event_id = soup.get("data-event-eventid")

            match_data["event_id"] = event_id

        except AttributeError:
            logger.error("Ошибка при парсинге!")
            with open("index.html", "w", encoding="utf-8") as file:
                file.write(str(soup))

            return None

        match_name = soup.find(class_=re.compile("coupon-row")).get("data-event-name")
        if match_name:
            match_data["match_name"] = match_name.strip()

        totals_common = await cls.get_table_values(soup_obj=soup, class_main="MATCH_TOTALS_SEVERAL_-")
        totals_first_team = await cls.get_table_values(soup_obj=soup, class_main="MATCH_TOTAL_FIRST_TEAM_")
        totals_first_team_1_time = await cls.get_table_values(
            soup_obj=soup, class_main="MATCH_TOTAL_FIRST_TEAM_1_")
        totals_first_team_2_time = await cls.get_table_values(
            soup_obj=soup, class_main="MATCH_TOTAL_FIRST_TEAM_2_")
        totals_second_team = await cls.get_table_values(soup_obj=soup, class_main="MATCH_TOTAL_SECOND_TEAM_")
        totals_second_team_1_time = await cls.get_table_values(
            soup_obj=soup, class_main="MATCH_TOTAL_SECOND_TEAM_1_")
        totals_second_team_2_time = await cls.get_table_values(
            soup_obj=soup, class_main="MATCH_TOTAL_SECOND_TEAM_2_")
        totals_2_time = await cls.get_table_values(soup_obj=soup, class_main="TOTALS_WITH_ODDEVEN2_")

        fore_win = await cls.get_table_values(
            soup_obj=soup, class_main="MATCH_HANDICAP_BETTING_COUPONE_DEPENDED_")
        fore_win_1_time = await cls.get_table_values(
            soup_obj=soup, class_main="FIRST_HALF_MATCH_HANDICAP_BETTING_")
        fore_win_2_time = await cls.get_table_values(
            soup_obj=soup, class_main="SECOND_HALF_MATCH_HANDICAP_BETTING_")

        match_data["totals_common"] = totals_common
        match_data["totals_first_team"] = totals_first_team
        match_data["totals_first_team_1_time"] = totals_first_team_1_time
        match_data["totals_first_team_2_time"] = totals_first_team_2_time
        match_data["totals_second_team"] = totals_second_team
        match_data["totals_second_team_1_time"] = totals_second_team_1_time
        match_data["totals_second_team_2_time"] = totals_second_team_2_time
        match_data["totals_2_time"] = totals_2_time
        match_data["fore_win"] = fore_win
        match_data["fore_win_1_time"] = fore_win_1_time
        match_data["fore_win_2_time"] = fore_win_2_time

        return match_data

    @classmethod
    async def parse_data_from_event_tennis(cls, soup: [BeautifulSoup, PageElement]):
        match_data = {}

        try:
            event_id = soup.find(class_=re.compile("coupon-row")).get("data-event-eventid")
            if not event_id:
                event_id = soup.get("data-event-eventid")

            match_data["event_id"] = event_id

        except AttributeError:
            logger.error("Ошибка при парсинге!")
            with open("index.html", "w", encoding="utf-8") as file:
                file.write(str(soup))

            return None

        match_data["event_id"] = event_id

        match_name = soup.find(class_=re.compile("coupon-row")).get("data-event-name")
        if match_name:
            match_data["match_name"] = match_name.strip()

        win_handicap_for_sets = await cls.get_table_values(soup_obj=soup, class_main="MATCH_HANDICAP_BETTING_SET_")
        win_handicap_for_games = await cls.get_table_values(soup_obj=soup, class_main="MATCH_HANDICAP_BETTING_GAME_")
        win_handicap_for_games_1_set = await cls.get_table_values(soup_obj=soup, class_main="SET_HANDICAP1_")

        totals_sets = await cls.get_table_values(soup_obj=soup, class_main="MATCH_TOTALS_SETS_")
        totals_games = await cls.get_table_values(soup_obj=soup, class_main="MATCH_TOTALS_GAMES_")
        totals_games_1_set = await cls.get_table_values(soup_obj=soup, class_main="TOTALS_WITH_ODDEVEN1_")

        match_data["totals_sets"] = totals_sets
        match_data["totals_games"] = totals_games
        match_data["totals_games_1_set"] = totals_games_1_set
        match_data["win_handicap_for_sets"] = win_handicap_for_sets
        match_data["win_handicap_for_games"] = win_handicap_for_games
        match_data["win_handicap_for_games_1_set"] = win_handicap_for_games_1_set

        return match_data
