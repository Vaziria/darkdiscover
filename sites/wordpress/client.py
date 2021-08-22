import json
import os
from common.persist import Persist
from common.http.session import CommonSession
from common.logger import Logger

logger = Logger(__name__)

class Client(Persist):
    host = {
        'base': 'https://wordpress.com',
        'api': 'https://public-api.wordpress.com',
        'api_v1': 'https://public-api.wordpress.com/rest/v1.1',
        'api_v2': 'https://public-api.wordpress.com/wp/v2'
    }

    loc: str
    
    email: str
    pwd: str
    session: CommonSession
    


    def __init__(self, email: str, pwd: str):

        self.loc = 'data/session/wordpress/{}'.format(email)
        self.email = email
        self.pwd = pwd

        if not self.load_obj():
            session = CommonSession(self.host)
            self.session = session
            self.session.default_header.update({
                'origin': 'https://wordpress.com'
            })
        
        else:
            self.session.host = self.host

    def login(self, force=False) -> bool:

        if not force:
            if os.path.exists(self.loc):
                return True

        payload = {
            "username": self.email,
            "password": self.pwd,
            "remember_me": "true",
            "redirect_to": "https://wordpress.com/",
            "client_id": 39911,
            "client_secret": "cOaYKdrkgXz8xY7aysv4fU6wL6sK5J8a6ojReEIAPwggsznj4Cb6mW0nffTxtYT8",
            "domain": "" 
        }
        
        res = self.session.post('/wp-login.php?action=login-endpoint', data=payload)

        if res.status_code == 200:
            hasil = res.json()
            if hasil['success'] == True:
                self.session.get('/')
            
            self.get_api_token()

            logger.info('[ {} ] logged'.format(self.email))
            self.save_obj()
            return True

        logger.error(res.status_code)
        logger.error(res.text)
        return False

    def get_api_token(self):

        res = self.session.get('/wp-admin/rest-proxy/?v=2.0', tipe='api')

        if res.status_code == 200:
            cookies = res.get_cookies()
            token = 'X-WPCOOKIE {}:1:https://wordpress.com'.format(cookies['wp_api'])
            self.session.default_header.update({
                'Authorization': token
            })

            self.save_obj()

            return True

        logger.error('[ {} ] getting api token error'.format(self.email))
        return False


if __name__ == '__main__':
    client = Client("manorder123@gmail.com", "santoso7777")
    print(client.login())
    print(client.session.default_header)
    # client.get_api_token()
    