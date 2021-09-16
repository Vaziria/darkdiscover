from lxml import etree

from common.persist_iter import iter_persist

from .client import Client
from .post import PostIterator

class StopPagination(Exception):
    pass

class ForumIterator:
    client: Client
    url: str
    path: str
    id: str
    page: int
    limit_page: int = 1

    def __init__(self, client: Client, url: str):
        self.client = client
        self.url = url
        self.get_data_from_url()

    def get_data_from_url(self):
        link = self.url.split('/')
        
        if link[-1].find('page') != -1:
            self.page = link[-1].replace('page-')
            self.page = int(self.page)

            self.path = link[-2]
        else:
            self.page = 1
            self.path = link[-1]
        
        self.id = self.path.split('.')[-1]

    def next_page_url(self):
        self.page += 1

        if self.page >  self.limit_page:
            raise StopPagination('paginasi tescapai')

        print('[ {} ] generating page {}'.format(self.client.email, self.page))

        url = self.client.host + '/forums/' + self.path + '/page-' + str(self.page)

        return url

    def get_page(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
        }

        res = self.client.session.get(url, headers=headers)
        
        if res.status_code != 200:
            return False

        hasil = etree.HTML(res.text)

        for forum in hasil.xpath('//div[@data-author]'):
            yield self.parse_forum(forum)

        if self.limit_page == 1:
            try:
                page = hasil.xpath('//li[@class="pageNav-page "]/a')[0]
                self.limit_page = int(page.text)
            except Exception as e:
                print(url)
    
    def parse_forum(self, forum: etree.HTML):
        url = forum.xpath('div/div/a[@data-preview-url]/@data-preview-url')[0]
        return self.client.host + url.replace('/preview', '')

    def iterate(self):

        for forum in self.get_page(self.url):
            yield forum

        while True:
            try:
                url = self.next_page_url()
                for forum in self.get_page(url):
                    yield forum

            except StopPagination as e:
                break

    def iterate_forum(self):
        @iter_persist(self.url)
        def forums():
            return self.iterate()

        for url in forums:
            print('[ {} ] iterating thread {}'.format(self.client.email, self.path))
            post = PostIterator(self.client, url)
            
            for conv in post.iterate():
                yield conv





if __name__ == '__main__':
    client = Client('seaseblues@gmail.com', 'bluefin1234')
    # client = Client('sweetestname013@gmail.com', 'heri7777')
    forum = ForumIterator(client, 'http://93.115.24.210/forums/film-cewek-indonesia-igo.11/')

    for data  in forum.iterate_forum():
        print(type(data.text))
