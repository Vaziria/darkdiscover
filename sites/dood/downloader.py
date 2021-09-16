import os
from selenium import webdriver
import requests
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class DoodDownloader:
    driver: webdriver.Chrome
    path_download: str

    def __init__(self, path_download: str):

        if not os.path.exists(path_download):
            os.makedirs(path_download)

        self.path_download = path_download

        options = webdriver.ChromeOptions() 
        options.add_argument("start-maximized")
        # options.add_argument("--headless")

        prefs = { "download.default_directory" : os.path.abspath("./")}
        options.add_experimental_option("prefs",prefs)

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        self.driver = webdriver.Chrome(options=options, executable_path="./chromedriver.exe")

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
       
    def download(self, link: str):
        self.driver.get(link)
        elem = self.driver.find_element_by_xpath('//h4')
        fname = elem.text

        elem = self.driver.find_element_by_xpath("//*[contains(text(), 'Download Now')]")
        elem.click()

        link = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".download-content > a")))
        lpdownload = link.get_attribute("href")
        self.driver.get(lpdownload)

        elem = self.driver.find_element_by_xpath("/html/body/div[1]/div/div/a")
        url = elem.get_attribute("onclick").replace("window.open('", '').replace("', '_self')", '')

        cookies = self.get_cookies()

        self.download_file(fname, url)

        return fname

if __name__ == '__main__':
    handler = DoodDownloader('data/download/')
    handler.download('https://dood.la/d/xmeo1g0h1h00')
