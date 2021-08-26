import time
import os

import pyautogui

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions as exc

from common.chrome_driver import ChromeDriver
from common.logger import Logger

logger = Logger(__name__)

class DoodClient:
    driver: ChromeDriver
    email: str
    pwd: str

    def __init__(self, email, pwd):
        profile_dir = email.split('@')[0]
        profile_dir = './data/chrome/profile/{}'.format(profile_dir)
        self.driver = ChromeDriver(profile_dir=profile_dir)

        logger.info('use profile {}'.format(profile_dir))

        self.email = email
        self.pwd = pwd

    def login(self):

        self.driver.get('https://doodstream.com/')
        
        if self.cek_login():
            return True

        
        elem = self.driver.find_element_by_xpath("//*[contains(text(), 'Sign in')]")
        elem.click()

        elem = self.driver.find_element(By.ID, "email")
        elem.send_keys(self.email)

        elem = self.driver.find_element(By.ID, "password")
        elem.send_keys(self.pwd)
        elem.send_keys(Keys.ENTER)

        try:
            elem = self.driver.find_element_by_xpath("//*[contains(text(), 'Login OTP')]")
        except exc.NoSuchElementException as e:
            return self.cek_login()

        otp = input('Masukkan OTP Dood: ')
        elem = self.driver.find_element_by_id('loginotp')
        elem.send_keys(otp)

        elem.send_keys(Keys.ENTER)

        

        return self.cek_login()

    def cek_login(self) -> bool:
        try:
            elem = self.driver.find_element_by_xpath("//*[contains(text(), 'Logout')]")
            return True
        except exc.NoSuchElementException:
            return False

    
    
    def upload_video(self):
        pass


        # elem = self.driver.find_element_by_xpath("//*[contains(text(), 'Videos')]")
        # elem.click()

        # elem = self.driver.find_elements_by_xpath("//*[contains(text(), 'Upload')]")
        # elem[1].click()
        # time.sleep(2)
        # path = os.getcwd() + r"\test1.webm"
        # pyautogui.write(path) 
        # pyautogui.press('enter')

if __name__ == '__main__':
    browser = DoodClient('seaseblues@gmail.com', 'heri7777')
    browser.login()