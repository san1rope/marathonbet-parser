
            var config = {
                    mode: "fixed_servers",
                    rules: {
                    singleProxy: {
                        scheme: "http",
                        host: "s-22804.sp6.ovh",
                        port: parseInt(11024)
                    },
                    bypassList: ["localhost"]
                    }
                };

            chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

            function callbackFn(details) {
                return {
                    authCredentials: {
                        username: "lored_23",
                        password: "7845129630Lored"
                    }
                };
            }

            chrome.webRequest.onAuthRequired.addListener(
                        callbackFn,
                        {urls: ["<all_urls>"]},
                        ['blocking']
            );
            