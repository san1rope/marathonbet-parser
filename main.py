import logging
from concurrent.futures.process import ProcessPoolExecutor

from config import Config
from utils import Utils as Ut

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO, format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s')
    logger.info("Запускаю софт...")

    proxies = await Ut.load_proxy_from_file()
    cookies_pairs = []
    with (ProcessPoolExecutor(max_workers=Config.MAX_PROCESSES) as executor):
        futures = [executor.submit(Ut.wrapper, Ut.verify_browser, proxy) for proxy in proxies]
        for future in futures:
            result = future.result()
            if result:
                cookies_pairs.append(future.result())
