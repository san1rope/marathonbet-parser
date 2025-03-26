import os

from pydantic import BaseModel


class Proxy(BaseModel):
    host: str
    port: int
    username: str
    password: str

    async def formulate_filename(self) -> str:
        return f"{self.host}_{self.port}_{self.username}_{self.password}"

    @staticmethod
    async def get_proxy_obj(proxy: str):
        host, port, username, password = proxy.split(":")
        return Proxy(host=host, port=port, username=username, password=password)

    async def create_proxy_extension(self):
        path = os.path.abspath("proxy-extensions\\" + await self.formulate_filename())
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
