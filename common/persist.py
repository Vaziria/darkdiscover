from typing import List
import pickle
import os
from hashlib import md5

from common.logger import Logger

logger = Logger(__name__)

class Persist:
    loc: str
    persist_exclude: List = []
    fresh = False

    def loc_not_exist(self):
        pass

    def gen_persistid(self, text):
        hasil = md5(text.encode('utf8'))

        return hasil.hexdigest()

    def save_obj(self):
        data = {}
        for key, value in self.__dict__.items():
            if key not in self.persist_exclude:
                data[key] = value

        with open(self.loc, 'w+b') as out:
            pickle.dump(data, out)

    def remove_obj(self):
        os.remove(self.loc)

    def load_obj(self):
        if not os.path.exists(self.loc):
            self.loc_not_exist()
            self.fresh = True
            return False
        try:
            with open(self.loc, 'rb') as out:
                data = pickle.load(out)
        except EOFError:
            data = {}
            logger.error('cannot load data {}'.format(self.loc), exc_info=True)

        self.__dict__.update(data)

        self.fresh = False
        return True

