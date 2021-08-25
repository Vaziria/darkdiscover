from typing import List
import enum

from common.logger import Logger

from .client import Client
from .tag import TagRepo
from .category import CategoryRepo

logger = Logger(__name__)

class StatusPost(enum.Enum):
    publish = 'publish'

class Post:
    id: int
    content: str
    status: StatusPost.publish
    title: str
    tags: List = []
    categories: List = []

    def __init__(self,
        id: int,
        content: str,
        status: str,
        title: str,
        tags: List = [],
        categories: List = []
    ):
        self.id = id
        self.content = content
        self.status = status
        self.title = title

        if tags:
            self.tags = tags

        if categories:
            self.categories = categories
        

class PostRepo:
    client: Client
    siteid: int
    tagRepo: TagRepo
    categRepo: CategoryRepo

    def __init__(self, client: Client, siteid: int, url:str, tagRepo: TagRepo, categRepo: CategoryRepo):
        self.client = client
        self.siteid = siteid
        self.url = url

        self.tagRepo = tagRepo
        self.categRepo = categRepo

    def get_id(self):
        res = self.client.session.get('{}/wp-admin/post-new.php'.format(self.url))
        html = res.html()
        inputs = html.xpath('//input[@name="post_ID"]/@value')
        
        return inputs[0]

    def publish(self, post: Post):
        if not post.id:
            post.id = self.get_id()
            logger.debug('[ {} ] publishing post {}'.format(self.client.email, post.id))

        if post.tags:
            tags = self.tagRepo.tags_to_id(post.tags)
            post.tags = tags

        if post.categories:
            categories = self.categRepo.category_to_id(post.categories)
            post.categories = categories
            
        query = {
            "_envelope": 1,
            "environment-id": 'production',
            # &_gutenberg_nonce=5d156db9cc&
            "_locale": "user"
        }
        path = '/sites/{}/posts/{}'.format(self.siteid, post.id)

        payload = post.__dict__

        res = self.client.session.put(path, tipe="api_v2", query=query, json=payload)
        if res.ok:
            self.client.save_obj()
            return res.json()

        logger.error('[ {} ] publish post {} error'.format(self.client.email, post.id))
        return False

if __name__ =='__main__':
    client = Client("manorder123@gmail.com", "santoso7777")
    client.login()

    tagRepo = TagRepo(client, 138105357)
    categRepo = CategoryRepo(client, 138105357)

    postr = PostRepo(client, 138105357, 'https://pdfzone2017.wordpress.com', tagRepo=tagRepo, categRepo=categRepo)

    content = """
    <p>aasdasdasd</p>\n<p><strong>test strong</strong></p>\n\n<!-- wp:html -->\n<iframe src=\"https://jomblo.org/file/asd/av2g/play\" scrolling=\"no\" frameborder=\"0\" width=\"700\" height=\"430\" allowfullscreen=\"true\" webkitallowfullscreen=\"true\" mozallowfullscreen=\"true\"></iframe>\t\n<!-- /wp:html -->\n\n<!-- wp:paragraph -->\n<p></p>\n<!-- /wp:paragraph -->
    """

    post = Post(
        None,
        content,
        StatusPost.publish.value,
        "blues test",
    )

    postr.publish(post)