from typing import Callable
from copy import deepcopy
from urllib.parse import urlencode
import json as jsonp

from requests import Session
from requests.models import Response
from lxml import etree

class CResponse:
    res: Response
    status_code: int
    ok: bool
    text: str

    def get_cookies(self):
        return self.res.cookies.get_dict()

    def __init__(self, res: Response):
        self.res = res

    def html(self)-> etree._Element:
        return etree.HTML(self.res.text.encode('utf8'))
    
    def __getattr__(self, name):
        return self.res.__getattribute__(name)


class CommonSession(Session):
    # hati hati bagian kode ini
    __attrs__ = [
        'headers', 'cookies', 'auth', 'proxies', 'hooks', 'params', 'verify',
        'cert', 'adapters', 'stream', 'trust_env',
        'max_redirects', 'default_header', 'host'
    ]

    default_header: dict = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    }

    host: dict

    def __init__(self, host):
        super().__init__()

        self.host = host
        self.default_header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
        }

        

    def generate_url(self, tipe, path, query):
        if query:
            query = '?' + urlencode(query)
        else:
            query = ''

        if path.find('http') != -1:
            return path + query

        if tipe:
            host = self.host.get(tipe)
        else:
            host = self.host.get('base', '')

        return host + path + query
        

    def inject_headers(self, argument):
        headers = deepcopy(self.default_header)

        if 'headers' in argument:
            headers.update(argument['headers'])
            argument['headers'] = headers

    def get(self, path, tipe=None, query=None, **kwargs) -> CResponse:
        url = self.generate_url(tipe, path, query)
        self.inject_headers(kwargs)
        
        res = super().get(url, **kwargs)

        return CResponse(res)

    def post(self, path, tipe=None, query=None, data=None, json=None, **kwargs) -> CResponse:
        url = self.generate_url(tipe, path, query)

        if json:
            kwargs['headers'] = {
                "content-type": "application/json"
            }
        self.inject_headers(kwargs)

        res = super().post(url, data, json, **kwargs)
        return CResponse(res)

    def put(self, path, tipe=None, query=None, data=None, json=None, **kwargs):
        url = self.generate_url(tipe, path, query)

        if json:
            data = jsonp.dumps(json)
            kwargs['headers'] = {
                "content-type": "application/json"
            }

        self.inject_headers(kwargs)

        res = super().put(url, data, **kwargs)
        return CResponse(res)