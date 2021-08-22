from typing import Generator
from itertools import cycle

from lxml import etree
from pyhtml import *

from common.persist import Persist
from common.logger import Logger
from crawler.sitemap import SitemapCrawler
from sites.wordpress.client import Client
from sites.wordpress.sites import SiteRepo, Site
from sites.wordpress.post import Post

logger = Logger(__name__)

class Upload(Persist):
    loc = 'data/BBindoWordpress.workflow'

    crawler: SitemapCrawler
    client: Client
    repo: SiteRepo
    links: Generator = False

    def __init__(self, email: str, pwd: str):
        if not self.load_obj():
            self.crawler = SitemapCrawler('http://23.234.240.172/sitemap_index.xml')
            
            client = Client(email, pwd)
            repo = SiteRepo(client)

            self.client = client
            self.repo = SiteRepo(client)
            
        
    def handler(self, xml: etree._Element):
        links = xml.xpath('//a/@href')
        for link in links:
            
            if link.find('streamtape') != -1:
                yield link

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
        sites = cycle(self.repo.get_sites())

        if not self.links:
            self.links = self.crawler.get_links()
        
        self.save_obj()

        return False

        for link in self.crawler.get_links():
            raw = self.crawler.get_page(link)

            site: Site = next(sites)

            for stlink in self.handler(raw):
                post = self.generate_post(link=stlink)
                site.postRepo.publish(post=post)

                logger.info('[ {} ] uploaded {} --> {}'.format(site.client.email, site.url, stlink))

                self.save_obj()

if __name__ == '__main__':
    
    upload = Upload("seaseblues@gmail.com", "bluefin1234")
    upload.run()