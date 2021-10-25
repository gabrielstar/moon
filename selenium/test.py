from selenium import webdriver
from time import sleep


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
        # options.add_argument('--headless')
        capabilities = {
            "browserName": "chrome",
            "selenoid:options": {
                "enableVNC": True,
                "enableVideo": False
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


# local
#driver = DriverFactory.create_driver('Chrome', False, '../drivers/chromedriver.exe')
# remote chrome - get IP from grid console
driver = DriverFactory.create_driver('Chrome', True, f'http://192.168.0.4:4444/wd/hub')
# moon
# driver = DriverFactory.create_driver('Chrome', True, f'http://20.103.25.207:4444/wd/hub')

driver.get('https://python.org')
print(driver.title)
assert driver.title == 'Welcome to Python.org'
sleep(5)
driver.quit()
