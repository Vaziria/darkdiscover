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

    save_start: bool


    def __init__(self, idname: str, handler: Callable, save_start = True):
        self.idname = idname
        self.save_start = save_start

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
            
            if self.save_start:
                self.save_obj()
                yield data
            
            else:
                yield data
                self.save_obj()
                
            
            

        self.remove_obj()


def iter_persist(name, **kwarg):
    def decorator(handler):
        return PersistIter(name, handler, **kwarg)

    return decorator



if __name__ == '__main__':

    @iter_persist('test')
    def test():
        for c in range(0, 10):
            yield c

    for data in test:
        print(data)
        
        if data == 3:
            break



