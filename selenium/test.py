from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys


class Chrome():
    capabilities = webdriver.DesiredCapabilities.CHROME.copy()

    def get_driver(self, url):
        return webdriver.Chrome(executable_path=url, desired_capabilities=self.capabilities)


class RemoteChrome():
    def get_driver(self, url):
        options = webdriver.ChromeOptions()
        options.add_argument("no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=800,600")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument('--headless')
        capabilities={
                "browserName": "chrome",
                "browserVersion": "93.0",
                "selenoid:options": {
                    "enableVNC": True,
                    "enableVideo": True
                }
            }
        driver = webdriver.Remote(
            command_executor=url,
            options=options,
            desired_capabilities=capabilities

        )
        return driver


class DriverFactory():
    @classmethod
    def create_driver(cls, type, remote, url):
        if not remote and type == 'Chrome':
            return Chrome().get_driver(url)
        elif remote and type == 'Chrome':
            return RemoteChrome().get_driver(url)


# test

#local_chrome_driver = DriverFactory.create_driver('Chrome', False, './drivers/chromedriver.exe')
#remote_chrome_driver = DriverFactory.create_driver('Chrome', True, f'http://192.168.0.10:4444/wd/hub')
moon_chrome_driver = DriverFactory.create_driver(
    'Chrome', True, f'http://20.101.234.149:4444/wd/hub')

driver = moon_chrome_driver
driver.get('https://python.org')
print(driver.title)
assert driver.title == 'Welcome to Python.org'
sleep(20)
driver.quit()
