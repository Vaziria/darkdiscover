from lxml import etree

from common.persist import Persist

from .client import Client

class StopPagination(Exception):
    pass

class PostIterator(Persist):

    loc: str
    persist_exclude = ['client']

    client: Client
    url: str
    path: str
    id: str
    page: int = 1
    limit_page: int = 1

    def __init__(self, client: Client, url: str):
        self.loc = 'data/persist/{}'.format(self.gen_persistid(url))

        if not self.load_obj():
            self.client = client
            self.url = url
            self.get_data_from_url()

        self.client = client

        

    def get_data_from_url(self):
        link = self.url.split('/')
        
        if link[-1].find('page') != -1:
            self.page = link[-1].replace('page-', '')
            self.page = int(self.page)

            self.path = link[-2]
        else:
            self.page = 1
            self.path = link[-1]
        
        self.id = self.path.split('.')[-1]

    def next_page_url(self):
        print('[ {} ] generating page {} {}'.format(self.client.email, self.path, self.page))

        if self.page > self.limit_page:
            raise StopPagination('paginasi tescapai')
        
        if self.page == 1:
            url = self.client.host + '/threads/' + self.path
        else:
            url = self.client.host + '/threads/' + self.path + '/page-' + str(self.page)

        self.page += 1

        return url

    def get_page(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
        }

        res = self.client.session.get(url, headers=headers)
        
        if res.status_code != 200:
            return False

        hasil = etree.HTML(res.text)

        for thread in hasil.xpath('//article'):
            yield thread

        if self.limit_page == 1:
            try:
                page = hasil.xpath('//li[@class="pageNav-page "]/a')[0]
                self.limit_page = int(page.text)
            except Exception as e:
                print('[ {} ] paginasi error'.format(self.client.email))

    def iterate(self):
        while True:
            try:
                url = self.next_page_url()
                for thread in self.get_page(url):
                    yield thread

            except StopPagination as e:
                break

            self.save_obj()

        self.remove_obj()





if __name__ == '__main__':
    client = Client('seaseblues@gmail.com', 'bluefin1234')
    client.login()
    post = PostIterator(client, 'http://93.115.24.210/threads/request-film-igo-di-sini-dilarang-rekues-video-underage-anak-sma-part-4.1389301')

    for thread in post.iterate():
        if thread.text.find('dood') != -1:
            print(thread.text)
