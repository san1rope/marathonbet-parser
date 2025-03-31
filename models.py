import os
from typing import Optional

from pydantic import BaseModel


class Proxy(BaseModel):
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None

    async def formulate_filename(self) -> str:
        name = f"{self.host}_{self.port}"
        if self.username is not None:
            name += f"_{self.username}_{self.password}"

        return name

    @staticmethod
    async def get_proxy_obj(proxy: str):
        proxy_list = proxy.split(":")
        if len(proxy_list) == 2:
            host, port = proxy_list
            username, password = None, None

        elif len(proxy_list) == 4:
            host, port, username, password = proxy_list

        else:
            return

        return Proxy(host=host, port=port, username=username, password=password)

    async def create_proxy_extension(self):
        path = os.path.abspath("proxy-extensions/" + await self.formulate_filename())
        try:
            os.mkdir(path)

        except FileExistsError:
            pass

        manifest_json = """
            {
                "version": "1.0.0",
                "manifest_version": 2,
                "name": "Proxies",
                "permissions": [
                    "proxy",
                    "tabs",
                    "unlimitedStorage",
                    "storage",
                    "<all_urls>",
                    "webRequest",
                    "webRequestBlocking"
                ],
                "background": {
                    "scripts": ["background.js"]
                },
                "minimum_chrome_version":"22.0.0"
            }
            """

        background_js = """
            var config = {
                    mode: "fixed_servers",
                    rules: {
                    singleProxy: {
                        scheme: "http",
                        host: "%s",
                        port: parseInt(%s)
                    },
                    bypassList: ["localhost"]
                    }
                };

            chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

            function callbackFn(details) {
                return {
                    authCredentials: {
                        username: "%s",
                        password: "%s"
                    }
                };
            }

            chrome.webRequest.onAuthRequired.addListener(
                        callbackFn,
                        {urls: ["<all_urls>"]},
                        ['blocking']
            );
            """ % (self.host, self.port, self.username, self.password)

        with open(path + "/manifest.json", 'w') as m_file:
            m_file.write(manifest_json)
        with open(path + "/background.js", 'w') as b_file:
            b_file.write(background_js)

    def __str__(self):
        return f"{self.host}:{self.port}"
