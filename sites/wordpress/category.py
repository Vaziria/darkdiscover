from typing import TypedDict, List
from common.logger import Logger

from .client import Client

logger = Logger(__name__)


class CategoryExistException(Exception):
    pass
class CategoryRepo:
    client: Client
    
    def __init__(self, client: Client, siteid: int):
        self.client = client
        self.siteid = siteid

    def create(self, category):
        path = '/sites/{}/categories'.format(self.siteid)
        query = {
            "_envelope": 1,
            "environment-id": "production",
            "_locale": "user"
        }

        payload = {
            "name": category
        }

        res = self.client.session.post(path, tipe='api_v2', query=query, json=payload)
        if res.ok:
            hasil = res.json()['body']

            if hasil.get('code') == 'term_exists':
                raise CategoryExistException('tag {} sudah ada'.format(category))

            return hasil

        raise Exception(res.text)

    def get(self, categ) -> List:
        path = '/sites/{}/categories'.format(self.siteid)
        query = {
            "_envelope": 1,
            "per_page": 20,
            "orderby": 'count',
            "order": "desc",
            "_fields": "id,name,count",
            "search": categ,
            "environment-id": "production",
            "_locale": "user"
        }

        res = self.client.session.get(path, tipe='api_v2', query=query)
        if res.ok:
            return res.json()['body']

        raise Exception(res.text)

    def category_to_id(self, categories: List[str]):
        hasil = []

        for category in categories:
            try:
                res = self.create(category)
            
            except CategoryExistException as e:
                res = self.get(category)
                res = res[0]

            hasil.append(res['id'])
        
        return hasil

if __name__ == '__main__':
    client = Client("manorder123@gmail.com", "santoso7777")
    client.login()
    repo = CategoryRepo(client, 138105357)

    print(repo.category_to_id(['love', 'theather']))