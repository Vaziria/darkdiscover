from requests import Session

from lxml import etree
from common.persist import Persist

class Client(Persist):
    loc: str
    email: str
    pwd: str

    session: Session
    host = 'http://93.115.24.210'
    # host = 'https://www.semprot.com'

    def __init__(self, email: str, pwd: str):

        self.email = email
        self.pwd = pwd
        self.session = Session()

        fname = email.split('@')[0]
        self.loc = 'data/session/{}'.format(fname)

        self.load_obj()

    def gurl(self, path):
        return self.host + path
    
    def loc_not_exist(self):
        if self.login():
            print('[ {} ] creating session login'.format(self.email))
            self.save_obj()
        else:
            print('[ {} ] gagal create session'.format(self.email))

    def login(self):
        headers = {
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-GB,en;q=0.9",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "sec-ch-ua-mobile": "?0",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
        }

        url = self.gurl("/login")
        res = self.session.get(url, headers=headers)
        
        if res.status_code != 200:
            return False
        
        elem = etree.HTML(res.text)
        token = elem.xpath('//input[@name="_xfToken"]/@value')[0]

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "http://93.115.24.210",
            "Pragma": "no-cache",
            "Referer": "http://93.115.24.210/login",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
        }
        
        data = {
            "login": "seaseblues@gmail.com",
            "password": "bluefin1234",
            "remember": "1",
            "_xfRedirect": "/",
            "_xfToken": token
        }

        url = self.gurl('/login/login')
        res = self.session.post(url, headers=headers, data=data)
        
        if res.status_code != 200:
            return False

        elem = etree.HTML(res.text)
        perca = elem.xpath('//*[@id="top"]/div[1]/nav/div/div[3]/div[1]/a[2]')

        if len(perca) > 0:
            return True

        return False

if __name__ == '__main__':
    auth = Client('seaseblues@gmail.com', 'bluefin1234')
