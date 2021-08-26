import time
import os

import pyautogui

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions as exc

from common.chrome_driver import ChromeDriver
from common.logger import Logger

logger = Logger(__name__)

class VideoRepo:
    driver: ChromeDriver

    def __init__(self, driver: ChromeDriver):
        self.driver = driver

    def upload(self, path):

        url = 'https://doodstream.com/videos'

        if self.driver.current_url != url:
            self.driver.get(url)
        
        elem = self.driver.find_elements_by_xpath("//*[contains(text(), 'Upload')]")
        elem[1].click()
        time.sleep(2)
        path = os.path.abspath(path)
        pyautogui.write(path) 
        pyautogui.press('enter')

if __name__ == '__main__':
    from .client import DoodClient

    browser = DoodClient('seaseblues@gmail.com', 'heri7777')
    # browser.login()

    repo = VideoRepo(browser.driver)
    path = 'data/test1.webm'
    repo.upload(path)