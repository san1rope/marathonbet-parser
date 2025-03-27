import asyncio
import logging
import os
import re

from aiohttp import BasicAuth, ClientSession
from bs4 import BeautifulSoup
from undetected_chromedriver import ChromeOptions, Chrome

from config import Config
from models import Proxy
from utils import Utils as Ut

logger = logging.getLogger(__name__)


async def main():
    proxy = Proxy(host="s-22494.sp6.ovh", port=11010, username="V4zH2d_9", password="hhNUPsJfpskT")
    cookie = ""

    proxy_ip = f"http://{proxy.host}:{proxy.port}"
    proxy_auth = BasicAuth(login=proxy.username, password=proxy.password)
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
        "cookie": f"cf_clearance=Zv9KONG0V9GZM.GxV7YJ_EjvZnoGdPaNbDmMp9qtn0E-1743062903-1.2.1.1-COVctVN5ZsOrLJjyQqfcJOuqqGpTEOdmGAJVGMyzt_uzX7Vrmkd43LTf9n5TCifV_sf2kJfvAFfJqhscd7q..kx6_ifIq8Wk68VP3fj3VlcstLGYGk9omOKpJon9VUcBNLsUxt4.JB2kDfShH1adla0roCQuf2QH2oJ0VuuVCbk1OlCgvdmE9aaVA.iqbyUt_kY.f5okxyPMfCGuSGtr79SA79eKFNGsWcSNNfLc.Shi95exkIUwU69HxfE70_vQon1ilQXoKd.QFjSCS4y7_mI2Wh8.kweYCGuN4CGstVQjk2znUk9pVFwhpsNa8b29ufaXgyKtEwgagonvdipt0Ujal9b0LTM76q4SFtYFNac_AKdDW4y9UZD0ZiB4shluBidlJ.A96K361iNup9bCwqinuZnw68.oAmRUYhs3fr4",
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
        page_url = f"https://www.marathonbet.com/su/betting/Football?page={1}"
        async with session.get(url=page_url, **request_default_kwargs) as response:
            soup_page = BeautifulSoup(await response.text(), "lxml")
            logger.info(f"Сделал запрос к странице: {page_url}")

        events_on_page = soup_page.find_all(class_="event-grid")
        for event in events_on_page:
            event_url = f"https://www.marathonbet.com" + event.find(class_="member-link").get("href")
            print(f"event_url = {event_url}")
            async with session.get(url=event_url, **request_default_kwargs) as response:
                soup_event = BeautifulSoup(await response.text(), "lxml")
                logger.info(f"Сделал запрос к ивенту: {event_url}")

            # totals
            totals_common = await Ut.get_table_values(soup_obj=soup_event, class_main="MATCH_TOTALS_SEVERAL_-")
            totals_first_team = await Ut.get_table_values(soup_obj=soup_event, class_main="MATCH_TOTAL_FIRST_TEAM_")
            totals_first_team_1_time = await Ut.get_table_values(
                soup_obj=soup_event, class_main="MATCH_TOTAL_FIRST_TEAM_1_")
            totals_first_team_2_time = await Ut.get_table_values(
                soup_obj=soup_event, class_main="MATCH_TOTAL_FIRST_TEAM_2_")
            totals_second_team = await Ut.get_table_values(soup_obj=soup_event, class_main="MATCH_TOTAL_SECOND_TEAM_")
            totals_second_team_1_time = await Ut.get_table_values(
                soup_obj=soup_event, class_main="MATCH_TOTAL_SECOND_TEAM_1_")
            totals_second_team_2_time = await Ut.get_table_values(
                soup_obj=soup_event, class_main="MATCH_TOTAL_SECOND_TEAM_2_")
            totals_2_time = await Ut.get_table_values(soup_obj=soup_event, class_main="TOTALS_WITH_ODDEVEN2_")

            fore_win = await Ut.get_table_values(
                soup_obj=soup_event, class_main="MATCH_HANDICAP_BETTING_COUPONE_DEPENDED_")
            fore_win_1_time = await Ut.get_table_values(
                soup_obj=soup_event, class_main="FIRST_HALF_MATCH_HANDICAP_BETTING_")
            fore_win_2_time = await Ut.get_table_values(
                soup_obj=soup_event, class_main="SECOND_HALF_MATCH_HANDICAP_BETTING_")

            print(f"common_totals = {totals_common}")
            print(f"first_team_totals = {totals_first_team}")
            print(f"totals_first_team_1_time = {totals_first_team_1_time}")
            print(f"totals_first_team_2_time = {totals_first_team_2_time}")
            print(f"second_team_totals = {totals_second_team}")
            print(f"totals_second_team_1_time = {totals_second_team_1_time}")
            print(f"totals_second_team_2_time = {totals_second_team_2_time}")
            print(f"totals_2_time = {totals_2_time}")
            print(f"----------------")
            print(f"fore_win = {fore_win}")
            print(f"fore_win_1_time = {fore_win_1_time}")
            print(f"fore_win_2_time = {fore_win_2_time}")

            await asyncio.sleep(2000)


if __name__ == "__main__":
    asyncio.run(main())
