import os
from itertools import cycle
import json
from urllib.parse import unquote

from lxml import etree
from pyhtml import *
from selenium.common.exceptions import NoSuchElementException

from common.logger import Logger
from crawler.sitemap import SitemapCrawler
from sites.wordpress.client import Client
from sites.wordpress.sites import SiteRepo, Site
from sites.wordpress.post import Post
from sites.streamtape.downloader import StreamtapeDownloader, PageData
from sites.dood.client import DoodClient
from sites.dood.video import VideoRepo

logger = Logger(__name__)

class Upload:

    crawler: SitemapCrawler
    streamtape_downloader: StreamtapeDownloader
    
    dood_video: VideoRepo
    dood_client: DoodClient

    client: Client
    repo: SiteRepo

    size: int = 100

    def __init__(self, email: str, pwd: str, doodpwd: str = None):

        if not doodpwd:
            doodpwd = pwd

        self.crawler = SitemapCrawler('http://23.234.240.172/sitemap_index.xml')
        self.streamtape = StreamtapeDownloader('data/download/')
        
        client = Client(email, pwd)
        repo = SiteRepo(client)

        self.client = client
        self.repo = SiteRepo(client)

        self.dood_client = DoodClient(email, doodpwd)
        self.dood_video = VideoRepo(self.dood_client.driver)

        self.streamtape_downloader = StreamtapeDownloader('data/download/')
        
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

            # if size > self.size:
            #     logger.info('size lebih besar {}'.format(link))
            #     continue

            yield data

    def generate_post(self, pagedata: PageData) -> Post:
        link = pagedata.url_page

        idnya = link.split('/')[-2]
        title = link.split('/')[-1].replace('_', ' ')
        title = unquote(title)

        iframe = '''
        <h2>{}</h2>
        <img src="{}" />
        <h3><a href="{}">Download</a></h3>
        '''.format(title, pagedata.thumbnail, pagedata.url_page)
        
        post = Post(
            None,
            content=iframe,
            status='publish',
            title=title
        )
        
        return post

    def upload(self, site: Site, pagedata: PageData):
        post = self.generate_post(pagedata)
        site.postRepo.publish(post=post)

        logger.info('[ {} ] uploaded {} --> {}'.format(site.client.email, site.url, pagedata.url_page))
        
    def run(self):

        self.client.login()
        # dood login
        self.dood_client.login()

        sites = cycle(self.repo.get_sites())

        for link in self.crawler.get_links():
            raw = self.crawler.get_page(link)
            site: Site = next(sites)

            for pagedata in self.handler(raw):
                pagedata: PageData = pagedata
                # download dulu
                location = self.streamtape_downloader.download(pagedata.url_page)

                # upload ke dood sendiri
                self.dood_video.upload(location)
                os.remove(location)

                self.upload(site, pagedata)

                

if __name__ == '__main__':
    
    upload = Upload("seaseblues@gmail.com", "bluefin1234")
    upload.run()