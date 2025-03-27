import asyncio
import logging
from concurrent.futures.process import ProcessPoolExecutor

from config import Config
from parser import new_task
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

        futures.clear()
        proxies_on_process = int(len(cookies_pairs) / Config.MAX_PROCESSES)

        start_index = 0
        while True:
            end_index = start_index + proxies_on_process
            new_future = executor.submit(Ut.wrapper, new_task, tuple(cookies_pairs[start_index:end_index]))
            futures.append(new_future)

            if end_index >= len(cookies_pairs):
                break

            start_index = end_index


if __name__ == "__main__":
    asyncio.run(main())
