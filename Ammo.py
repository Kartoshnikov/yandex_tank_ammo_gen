from requests.exceptions import BaseHTTPError

CTRL = '\r\n'

class Ammo:
    def __init__(self):
        self.__type = ''
        self.__httpVer = ''
        self.__agent = ''
        self.__host = ''
        self.__cookie = ''
        self.__url = ''
        self.__accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'

    def format(self):
        head = f"{self.type} {self.url} HTTP/{self.httpVer}{CTRL}" \
               f"Host: {self.host}{CTRL}" \
               f"Content-Length: {len(self.body.decode(encoding='utf-8')) if self.body else '0'}{CTRL}" \
               f"Connection: close{CTRL}" \
               f"{self.cookie}{CTRL}" \
               f"Accept: {self.__accept}{CTRL}" \
               f"Pragma: no-cache{CTRL}" \
               f"Accept-Encoding: gzip, deflate, br{CTRL}r" \
               f"Accept-Language: en-US,en;q=0.9{CTRL}" \
               f"User-Agent: {self.agent}{CTRL*2}"
        if self.body:
            head += f"{self.body}{CTRL}"
        com_length = len(head)
        key = self.url
        for char in ['/', '&', '?', '=', '%5B', '%5D']:
            key = key.replace(char, '_')
        return f"{com_length} {key}\n{head}"

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        self.__type = value

    @property
    def httpVer(self):
        return self.__httpVer

    @httpVer.setter
    def httpVer(self, value):
        self.__httpVer = value

    @property
    def agent(self):
        return self.__agent

    @agent.setter
    def agent(self, value):
        self.__agent = value

    @property
    def host(self):
        return self.__host

    @host.setter
    def host(self, value):
        self.__host = value

    @property
    def cookie(self):
        return self.__cookie

    @cookie.setter
    def cookie(self, value):
        self.__cookie = value

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, value):
        self.__url = value

    @property
    def body(self):
        try:
            return self.__body
        except AttributeError:
            return False

    @body.setter
    def body(self, value):
        self.__body = value
