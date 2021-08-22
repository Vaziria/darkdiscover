from typing import List

from lxml import etree
import requests

from common.logger import Logger

logger = Logger(__name__)

class SitemapCrawler:
    url: str
    http: requests.Session

    def __init__(self, url: str, httphandler: requests.Session = None):
        self.url = url

        if httphandler:
            self.http = httphandler
        else:
            self.http = requests.Session()

    def get_links(self, url: str = None):
        if not url:
            url = self.url

        res = self.http.get(url)
        
        if res.status_code != 200:
            logger.error('error xml {}'.format(url))

        xml: etree._Element = etree.HTML(res.text.encode('utf8'))

        for link in xml.xpath('//loc/text()'):
            if link[-4:] == '.xml':
                for linkc in self.get_links(link):
                    if linkc[-4:] != '.jpg':
                        yield linkc

                continue

            yield link
    
    def get_page(self, url: str):
        res = self.http.get(url)
        xml: etree._Element = etree.HTML(res.text.encode('utf8'))
        return xml
        


        
if __name__ == '__main__':
    crawler = SitemapCrawler('http://23.234.240.172/sitemap_index.xml')

    def handler(xml: etree._Element):
        links = xml.xpath('//a/@href')
        for link in links:
            
            if link.find('streamtape') != -1:
                yield link

    for link in crawler.get_links():
        raw = crawler.get_page(link)

        for stlink in handler(raw):
            print(stlink)


    

    