import os
import requests
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException, TimeoutException

from common.logger import Logger
from common.chrome_driver import ChromeDriver

executable_path = os.environ.get('selenium_driver', '')

logger = Logger(__name__)

class PageData:
    fname: str
    url: str
    size: int
    thumbnail: str
    url_page: str

class StreamtapeDownloader:
    driver: ChromeDriver
    path_download: str

    def __init__(self, path_download: str):

        if not os.path.exists(path_download):
            os.makedirs(path_download)

        self.path_download = path_download
        self.driver = ChromeDriver()

    def get_cookies(self):
        cookies = {}
        for cookie in self.driver.get_cookies():
            cookies[cookie['name']] = cookie['value']

        return cookies

    def download_file(self, fname, url):
        cookies = self.get_cookies()
        headers = {
            "Referer": "https://dood.la/",
            "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            'sec-ch-ua-mobile': "?0",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
        }
        
        local_filename = self.path_download + fname + '.mp4'
        # NOTE the stream=True parameter below
        with requests.get(url, stream=True, cookies=cookies, headers=headers) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    #if chunk: 
                    f.write(chunk)
        return local_filename

    def close_iklan(self):
        for handler in self.driver.window_handles:
            self.driver.switch_to.window(handler)
            try:
                url = self.driver.current_url
            except UnexpectedAlertPresentException:
                continue
            
            if url.find('streamtape') == -1:
                self.driver.close()
        
        handler = self.driver.window_handles[0]
        self.driver.switch_to.window(handler)

    def get_data(self) -> PageData:
        elem = self.driver.find_element_by_xpath('//h2')
        fname = elem.text

        # click close
        try:
            elem = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="_vlwsig "]/div')))
            elem.click()
        except TimeoutException:
            pass

        self.close_iklan()

        for c in range(0, 100):
            try:
                elem = self.driver.find_element_by_xpath("//*[contains(text(), 'Download Video')]")
                elem.click()
            except Exception as e:
                logger.debug('tombol download video notfound')

            self.close_iklan()

            link = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#downloadvideo")))
            url = link.get_attribute("href")
            
            if url.find('/get_video?') != -1:
                break
        
        elem = self.driver.find_element_by_xpath('//video[@id="mainvideo"]')
        thumbnail = elem.get_attribute('poster')

        data = PageData()
        data.fname = fname
        data.url = url
        data.size = self.get_size()
        data.thumbnail = thumbnail
        data.url_page = self.driver.current_url
        
        return data
    
    def get_size(self):

        elem = self.driver.find_element_by_xpath('//p[@class="subheading"]')
        text = elem.get_attribute('innerHTML')
        if text.find('GB') != -1:
            text = text.replace('GB', '').replace(' ', '').replace(',', '')
            size = float(text) * 1000
        else:
            text = text.replace('MB', '').replace(' ', '').replace(',', '')
            size = float(text)

        return size

    def download(self, link: str):
        self.driver.get(link)
        data = self.get_data(link)

        self.download_file(data.fname, data.url)

        return data.fname

if __name__ == '__main__':
    handler = StreamtapeDownloader('data/download/')
    handler.driver.get('https://streamtape.com/v/12qzbVdp2gfdmK/Russian_Anal_Casting_with_Flick_Luchik%2C_Balls_Deep_Anal%2C_Gapes_and_Swallow_GL257-23072020.mp4')
    size = handler.get_size()
    data = handler.get_data()

    print(size)
    print(data.__dict__)
