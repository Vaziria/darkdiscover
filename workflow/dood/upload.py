import os
import time

from lxml import etree

from sites.forum46.client import Client
from sites.forum46.post import PostIterator
from sites.dood.client import DoodClient
from sites.dood.video import VideoRepo
from sites.streamtape.downloader import StreamtapeDownloader, PageData

from common.logger import Logger

logger = Logger(__name__)


class DataRepo:
    datas = []
    def add(self, data):
        if data not in self.datas:
            self.datas.append(data)
            return True
        
        return False

    def exist(self, data):
        return data in self.datas

class Main:
    streamtape_downloader: StreamtapeDownloader
    dood_video: VideoRepo
    dood_client: DoodClient

    data_repo: DataRepo

    def __init__(self, email: str, pwd: str, doodpwd: str = None):

        if not doodpwd:
            doodpwd = pwd

        self.streamtape_downloader = StreamtapeDownloader('data/download/')

        self.data_repo = DataRepo()
        self.dood_client = DoodClient(email, doodpwd)
        self.dood_video = VideoRepo(self.dood_client.driver)

    def download(self, url):
        logger.info('[ downloading ] {}'.format(url))
        # download dulu
        location = self.streamtape_downloader.download(url)

        # upload ke dood sendiri
        self.dood_video.upload(location)
        # os.remove(location)


    def run(self):

        client = Client('seaseblues@gmail.com', 'bluefin1234')
        client.login()
        post = PostIterator(client, 'http://93.115.24.210/threads/bongkar-koleksi-asia-update-2-september-2021.1390376')

        thread: etree._Element
        for thread in post.iterate():
            links = thread.xpath('//a')
            
            for link in links:
                url = link.attrib.get('href', '')
                if url.find('streamtape') == -1:
                    continue
                
                if not self.data_repo.add(url):
                    continue

                self.download(url)
                logger.info('[ finish ] {}'.format(url))
                    


if __name__ == '__main__':
    runner = Main("seaseblues@gmail.com", "bluefin1234")
    runner.run()