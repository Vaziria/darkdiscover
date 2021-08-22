from typing import TypedDict, List
from common.logger import Logger

from .client import Client

logger = Logger(__name__)

class TagExistException(Exception):
    pass

class Tag(TypedDict):
    id: int
    name: str
    count: int

class TagRepo:
    def __init__(self, client: Client, siteid: int):
        self.client = client
        self.siteid = siteid

    def get_tag(self, keyword) -> List[Tag]:
        path = '/sites/{}/tags'.format(self.siteid)
        query = {
            "_envelope": 1,
            "per_page": 20,
            "orderby": 'count',
            "order": "desc",
            "_fields": "id,name,count",
            "search": keyword,
            "environment-id": "production",
            "_locale": "user"
        }

        res = self.client.session.get(path, tipe='api_v2', query=query)
        if res.ok:
            return res.json()['body']

        raise Exception(res.text)

    def create_tag(self, keyword):
        path = '/sites/{}/tags'.format(self.siteid)
        query = {
            "_envelope": 1,
            "environment-id": "production",
            "_locale": "user"
        }

        payload = {
            "name": keyword
        }

        res = self.client.session.post(path, tipe='api_v2', query=query, json=payload)
        if res.ok:
            hasil = res.json()['body']

            if hasil.get('code') == 'term_exists':
                raise TagExistException('tag {} sudah ada'.format(keyword))

            return hasil

        raise Exception(res.text)

    def tags_to_id(self, tags: List[str]):
        hasil = []

        for tag in tags:
            try:
                res = self.create_tag(tag)
            
            except TagExistException as e:
                res = self.get_tag(tag)
                res = res[0]

            hasil.append(res['id'])

        return hasil
        

if __name__ == '__main__':
    client = Client("manorder123@gmail.com", "santoso7777")
    client.login()
    repo = TagRepo(client, 138105357)

    print(repo.get_tag('jikaku'))
    # print(repo.create_tag('black'))

    print(repo.tags_to_id(['tas', 'beatbox', 'often']))
