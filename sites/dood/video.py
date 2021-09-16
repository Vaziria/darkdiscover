import time
import os
import random

import pyautogui

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions as exc
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from common.chrome_driver import ChromeDriver
from common.logger import Logger

logger = Logger(__name__)

class VideoRepo:
    driver: ChromeDriver

    def __init__(self, driver: ChromeDriver):
        self.driver = driver

    def upload(self, path):

        url = 'https://doodstream.com/videos'

        # if self.driver.current_url != url:
        self.driver.get(url)
        
        elem = self.driver.find_elements_by_xpath("//button[contains(text(), 'Upload')]")
        elem[0].click()
        # open = """
        # function getElementByXpath(path) {
        #     return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        # }
        # getElementByXpath("//button[contains(text(), 'Upload')]").click()
        # """
        # self.driver.execute_script(open)

        time.sleep(2)
        path = os.path.abspath(path)
        pyautogui.write(path)
        time.sleep(random.randint(1, 5))
        pyautogui.press('enter')

    def get_file_url(self, name: str):
        link = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//h4/a')))

        elems = self.driver.find_elements_by_xpath('//h4/a')
        for elem in elems:
            if elem.text.find(name) != -1:
                return elem.get_attribute('href')

if __name__ == '__main__':
    from .client import DoodClient

    browser = DoodClient('seaseblues@gmail.com', 'heri7777')
    # browser.login()

    repo = VideoRepo(browser.driver)
    # path = './data/download/test.mp4'
    # repo.upload(path)

    repo.driver.get('https://doodstream.com/videos')

    url = repo.get_file_url('test1')
    print('url data', url)