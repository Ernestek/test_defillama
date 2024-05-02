import csv
import json
import time

import requests
from selenium.common import NoSuchElementException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


class Defillama:
    BASE_URL = 'https://defillama.com/chains'
    csv_file = 'data.csv'

    def __init__(self, proxy=None):

        browser_options = ChromeOptions()
        service_args = [
            # '--headless=True'
            '--start-maximized',
            '--no-sandbox',
            '--disable-web-security',
            '--disable-blink-features=AutomationControlled',
            '--allow-running-insecure-content',
            '--hide-scrollbars',
            '--disable-setuid-sandbox',
            '--profile-directory=Default',
            '--ignore-ssl-errors=true',
            '--disable-dev-shm-usage',
        ]
        for arg in service_args:
            browser_options.add_argument(arg)
        browser_options.add_experimental_option(
            'excludeSwitches', ['enable-automation']
        )
        browser_options.add_experimental_option('prefs', {
            'profile.default_content_setting_values.notifications': 2,
            'profile.default_content_settings.popups': 0
        })
        browser_options.add_experimental_option('useAutomationExtension', False)
        if proxy:
            browser_options.add_argument(f'--proxy-server={proxy}')

        self.driver = Chrome(options=browser_options, )

    def placer_proton_mail_auto(self):
        self.driver.get(self.BASE_URL)

        self._wait_and_choose_element('[class="sc-58cbf52a-0 hisyWy"] > div:nth-of-type(2) > div')
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        items = self.driver.find_elements(by=By.CSS_SELECTOR,
                                          value='[class="sc-58cbf52a-0 hisyWy"] > div:nth-of-type(2) > div')

        try:
            old_item = int(items[-1].find_element(By.CSS_SELECTOR, '[class="sc-f61b72e9-0 iphTVP"] span').text) + 1
        except (NoSuchElementException, AttributeError):
            return

        while True:
            items = self.driver.find_elements(By.CSS_SELECTOR,
                                              '[class="sc-58cbf52a-0 hisyWy"] > div:nth-of-type(2) > div')
            for item in reversed(items):
                if old_item > int(item.find_element(By.CSS_SELECTOR, '[class="sc-f61b72e9-0 iphTVP"] span').text):
                    item_num = item.find_element(By.CSS_SELECTOR, '[class="sc-f61b72e9-0 iphTVP"] span').text
                    old_item = int(item_num)
                    self.get_info_one_item(item, item_num)
            self.driver.execute_script('window.scrollBy(0, -500);')
            time.sleep(0.5)
            if old_item == 1:
                break

    def get_info_one_item(self, item: WebElement, num) -> None:
        try:
            name = item.find_element(By.CSS_SELECTOR, '[class="sc-f61b72e9-0 iphTVP"] a').text
        except (NoSuchElementException, AttributeError):
            name = item.find_element(By.CSS_SELECTOR, '[class="sc-f61b72e9-0 iphTVP"] span').text
        try:
            protocols = item.find_element(By.CSS_SELECTOR, '[class="sc-58cbf52a-1 hehOwR"]:nth-of-type(2)').text
        except (NoSuchElementException, AttributeError):
            protocols = None
        try:
            tvl = item.find_element(By.CSS_SELECTOR, '[class="sc-58cbf52a-1 hehOwR"]:nth-of-type(7)').text
        except (NoSuchElementException, AttributeError):
            tvl = None
        data = (name, protocols, tvl)
        print(data)
        with open(self.csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)

    def _wait_and_choose_element(self, selector: str, by: By = By.CSS_SELECTOR, timeout: int = 4) -> WebElement:
        condition = EC.presence_of_element_located((by, selector))
        element = WebDriverWait(self.driver, timeout).until(condition)
        return element

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()


if __name__ == '__main__':
    with open('config.json', 'r') as file:
        config = json.load(file)

    interval = config['interval_minutes'] * 60
    proxy = config['proxy']

    def check_proxy(proxy):
        try:
            response = requests.get('http://example.com', proxies={'http': proxy, 'https': proxy}, timeout=5)
            if response.status_code == 200:
                print(f'Proxy {proxy} работает.')
                return True
            else:
                print(f'Proxy {proxy} dont work, status code: {response.status_code}')
                return False
        except Exception as e:
            print(f'Proxy {proxy} error: {e}')
            return False

    if (check_proxy(proxy)):
        while True:
            with Defillama() as placer:
                try:
                    placer.placer_proton_mail_auto()
                except Exception as error:
                    print(error)
                time.sleep(interval)
