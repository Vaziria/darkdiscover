from common.logger import Logger

from .client import Client

logger = Logger(__name__)

class Post:
    id: int = None
    client: Client

    def __init__(self, client: Client):
        self.client = client

    def get_id(self):
        res = self.client.session.get('https://pdfzone2017.wordpress.com/wp-admin/post-new.php')
        html = res.html()
        inputs = html.xpath('//input[@name="post_ID"]/@value')
        
        return inputs[0]

    def publish(self):
        if not self.id:
            self.id = self.get_id()
            logger.debug('[ {} ] publishing post {}'.format(self.client.email, self.id))
            

        query = {
            "_envelope": 1,
            "environment-id": 'production',
            # &_gutenberg_nonce=5d156db9cc&
            "_locale": "user"
        }
        path = '/sites/138105357/posts/{}'.format(self.id)

        payload = {
            "content": "test",
            "id": self.id,
            "status": "publish",
            "title": "hansoltest"
        }

        res = self.client.session.put(path, tipe="api_v2", query=query, json=payload)
        print(res.text)

if __name__ =='__main__':
    client = Client("manorder123@gmail.com", "santoso7777")
    if client.fresh:
        client.login()

    post = Post(client)
    post.publish()