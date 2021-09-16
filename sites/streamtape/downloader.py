import os
import time
from uuid import uuid4
import re

import requests
from lxml import etree
from tqdm import tqdm
from urllib.parse import unquote
from common.logger import Logger
from common.http.session import CommonSession

executable_path = os.environ.get('selenium_driver', '')

logger = Logger(__name__)

class PageData:
    fname: str
    url: str
    size: int
    thumbnail: str
    url_page: str

class StreamtapeDownloader:
    path_download: str

    def __init__(self, path_download: str):

        if not os.path.exists(path_download):
            os.makedirs(path_download)

        self.path_download = path_download

    def download_file(self, fname, url, cookies):
        headers = {
            "Origin": "https://streamtape.com",
            "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            'sec-ch-ua-mobile': "?0",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
        }
        
        local_filename = self.path_download + fname
        # NOTE the stream=True parameter below
        size = 0
        bar = None
        chunk_size = 8192
        with requests.get(url, stream=True, headers=headers, cookies=cookies) as r:

            if size == 0:
                size = int(r.headers.get('Content-length'))
                bar = tqdm(range(size))
                
        

            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=chunk_size): 
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    #if chunk: 
                    f.write(chunk)
                    # try:
                    bar.update(chunk_size)
                    # except Exception:
                    #     pass

        return local_filename 

    def download(self, link: str):
        fname = unquote(link).split('/')[-1]

        session = CommonSession({})
        res = session.get(link)
        
        if res.status_code != 200:
            logger.error('gagal {}'.format(link))

        data = etree.HTML(res.text)
        links = data.xpath('//div[@id="videoolink"]')
        link = 'https:' + links[0].text

        pola = re.compile(r'token\=([a-zA-Z0-9\_\-]*)')

        scripts = data.xpath('//script')
        for script in scripts:
            if script.text == None:
                continue

            if script.text.find("document.getElementById('videoolink')") == -1:
                continue
            
            tokens = pola.findall(script.text)
            if len(tokens) > 0:
                link = pola.sub('token=' + tokens[0], link) + '&dl=1'
                break
        
        cookies = session.cookies.get_dict()
        self.download_file(fname, link, cookies)
        return self.path_download + fname

if __name__ == '__main__':
    handler = StreamtapeDownloader('data/download/')
    url = 'https://streamtape.com/v/12qzbVdp2gfdmK/Russian_Anal_Casting_with_Flick_Luchik%2C_Balls_Deep_Anal%2C_Gapes_and_Swallow_GL257-23072020.mp4'
    handler.download(url)
    # size = handler.get_size()
    # data = handler.get_data()

    # print(size)
    # print(data.__dict__)
