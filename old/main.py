import asyncio
import logging
from concurrent.futures.process import ProcessPoolExecutor

from config import Config, PROXIES
from parser import start_parser
from utils import Utils as Ut

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO, format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s')
    logger.info("Запускаю софт...")

    load_proxies = await Ut.load_proxy_from_file()
    with (ProcessPoolExecutor(max_workers=Config.MAX_BROWSERS) as executor):
        futures = [executor.submit(Ut.wrapper, Ut.verify_browser, proxy) for proxy in load_proxies]
        for future in futures:
            result = future.result()
            if result:
                PROXIES.append(result)
    
    tasks = [asyncio.create_task(start_parser(page_start=i)) for i in range(1, Config.MAX_ASYNC_THREADS + 1)]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
