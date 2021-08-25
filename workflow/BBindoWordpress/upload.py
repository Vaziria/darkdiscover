from itertools import cycle
import json

from lxml import etree
from pyhtml import *
from selenium.common.exceptions import NoSuchElementException

from common.logger import Logger
from crawler.sitemap import SitemapCrawler
from sites.wordpress.client import Client
from sites.wordpress.sites import SiteRepo, Site
from sites.wordpress.post import Post
from sites.streamtape.downloader import StreamtapeDownloader

logger = Logger(__name__)

class Upload:

    crawler: SitemapCrawler
    streamtape: StreamtapeDownloader
    client: Client
    repo: SiteRepo

    size: int = 100

    def __init__(self, email: str, pwd: str):

        self.crawler = SitemapCrawler('http://23.234.240.172/sitemap_index.xml')
        self.streamtape = StreamtapeDownloader('data/download/')
        
        client = Client(email, pwd)
        repo = SiteRepo(client)

        self.client = client
        self.repo = SiteRepo(client)
            
        
    def handler(self, xml: etree._Element):
        links = xml.xpath('//a/@href')
        for link in links:
            
            if link.find('streamtape') == -1:
                continue
            
            self.streamtape.driver.get(link)
            try:
                size = self.streamtape.get_size()
            except NoSuchElementException:
                logger.info('link error {}'.format(link))
                continue

            data = self.streamtape.get_data()
            with open('dump.txt', 'a+') as out:
                out.write(json.dumps(data.__dict__)+'\n')

            if size > self.size:
                logger.info('size lebih besar {}'.format(link))
                continue

            yield data

    def generate_post(self, link) -> Post:
        idnya = link.split('/')[-2]
        title = link.split('/')[-1].replace('_', ' ')

        iframe = '<strong>{}</strong><iframe src="https://streamtape.com/e/{}/" width="800" height="600" allowfullscreen allowtransparency allow="autoplay" scrolling="no" frameborder="0"></iframe>'.format(title, idnya)
        
        
        post = Post(
            None,
            content=iframe,
            status='publish',
            title=title
        )
        
        return post

        
    def run(self):

        self.client.login()

        # sites = cycle(self.repo.get_sites())

        for link in self.crawler.get_links():
            raw = self.crawler.get_page(link)
            # site: Site = next(sites)

            for stlink in self.handler(raw):
                logger.info(stlink)

                # post = self.generate_post(link=stlink)
                # site.postRepo.publish(post=post)

                # logger.info('[ {} ] uploaded {} --> {}'.format(site.client.email, site.url, stlink))

if __name__ == '__main__':
    
    upload = Upload("seaseblues@gmail.com", "bluefin1234")
    upload.run()