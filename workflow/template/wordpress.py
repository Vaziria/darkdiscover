from abc import ABC, abstractmethod

class Repo(ABC):
    pass

class main(ABC):

    repo: Repo
    upload_handler: Repo

    @abstractmethod
    def run(self):
        pass