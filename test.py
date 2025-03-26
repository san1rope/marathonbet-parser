import asyncio
import os

from undetected_chromedriver import ChromeOptions, Chrome

from config import Config


async def main():
    options1 = ChromeOptions()
    options2 = ChromeOptions()

    driver1 = Chrome(options=options1)
    driver2 = Chrome(options=options2)

    await asyncio.sleep(10)

    driver1.quit()
    driver2.quit()


if __name__ == "__main__":
    asyncio.run(main())
