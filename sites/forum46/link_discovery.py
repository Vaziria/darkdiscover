from typing import List, IO, Callable
import os
from hashlib import md5
import json

from common.persist import Persist
from .client import Client
from .forum import ForumIterator

class LinkDiscovery(Persist):

    persist_exclude = ['writer', 'handler']
    chunk_c: int = 0
    chuck_limit: int = 10

    email: str
    pwd: str
    loc: str
    
    client: Client
    forums: List[ForumIterator]

    writer: IO
    handler: Callable

    def __init__(self, email: str, pwd: str, forums: List[str], writer: IO, handler: Callable):
        fname = self.get_hash_name()
        self.loc = 'data/link_discover_state/{}'.format(fname)

        if os.path.exists(self.loc):
            self.load_obj()
        
        else:
            self.client = Client(email, pwd)
            self.forums = list(map(lambda link: ForumIterator(client, link), forums))

        self.email = email
        self.pwd = pwd
        self.writer = writer
        self.handler = handler
    
    def get_hash_name(self, forums: List[str]):
        raw = json.dumps(forums.sort())
        has = md5(raw)

        return has.hexdigest()

    def check_saving_chuck(self):
        self.chunk_c += 1

        if self.chunk_c > self.chuck_limit:
            self.save_obj()
            print('saving chunk')
            self.chunk_c = 0

    def run(self):

        for forum in self.forums:
            for data in forum.iterate_forum():
                line = self.handler(data)
                self.writer.write(line + '\n')

                self.check_saving_chuck()

if __name__ == '__main__':

    def handler(data):
        text = data.text

        print(type(data))
    

    with open('data/hasil_link.txt', 'a+') as out:
        discover = LinkDiscovery('seaseblues@gmail.com', 'bluefin1234', [
            ''
        ], out, handler)

        discover.run()

