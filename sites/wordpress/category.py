from .client  import Client

class Category:
    client: Client
    
    def __init__(self, client: Client):
        self.client = client

    def create(self):
        pass