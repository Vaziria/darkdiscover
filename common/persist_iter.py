import os
from hashlib import md5

from typing import Callable, List

from .persist import Persist

class PersistIter(Persist):
    loc: str
    persist_exclude = ['handler', 'idname']
    idname: str

    handler: Callable
    data: List


    def __init__(self, idname: str, handler: Callable):
        self.idname = idname

        fname = self.create_fname()
        self.loc = 'data/persist_iter/{}'.format(fname)
        self.handler = handler

        self.load_obj()

    def create_fname(self):
        fname = __name__ + os.path.realpath(__file__) + self.idname
        hash = md5(fname.encode('utf8'))

        return str(hash.hexdigest())

    
    def loc_not_exist(self):
        self.data = list(self.handler())
        self.save_obj()

    def __iter__(self):
        if not self.data:
            self.data = self.handler()
            self.save_obj()
        
        while True:
            try:
                data = self.data.pop(0)
            except IndexError as e:
                break
            
            self.save_obj()
            yield data
            

        self.remove_obj()


def iter_persist(handler):
    pass



if __name__ == '__main__':

    def test():
        for c in range(0, 10):
            yield c
    
    persist = PersistIter('test', test)

    for data in persist:
        print(data)
        
        if data == 3:
            break



