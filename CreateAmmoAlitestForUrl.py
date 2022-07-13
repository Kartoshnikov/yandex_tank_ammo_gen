import os
import json
import requests
import multiprocessing as m
from lxml.html import fromstring
from queue import Empty
from random import shuffle
from Ammo import Ammo


class AmmoAlitest:
    def __init__(self):
        self.__sessions = {}
        self.__result = []
        self.__input_queue = m.JoinableQueue()
        self.__output_queue = m.Queue()
        self.packets_per_role_department = 2
        self.__input = [
            ['Student', '/', 50, 0],
            ['Teacher', '/', 50, 0],
        ]
        self.ammo = Ammo()
        self.host = 'devapp.example.com'
        self.file = 'tank/devapp.example.com.yml.amo.txt'
        self.servers = [
            '434',
            '123',
            '754',
            '752',
            '974',
            '184',
            '343',
            '534',
        ]

    def run(self):
        self.ammo = Ammo()
        self.__get_sessions()
        self.ammo.type = 'GET'
        self.ammo.httpVer = '1.1'
        self.ammo.agent = 'Tank/1.9.1'
        self.ammo.host = self.host
        self.__prepare_data()
        self.__build_ammo_file()

    def __build_ammo_file(self):
        with open(self.file, 'w') as ammo_file:
            ammo_file.write('')
        for step in self.__result:
            self.ammo.cookie = f'Cookie: {step["session"]}'
            self.ammo.url = f"{step['link']}{'&' if '?' in step['link'] else  '?'}s={step['index']}"
            self.__add_ammo_to_file(self.ammo, self.file)

    def __get_sessions(self):
        cache = {}
        for server in self.servers:
            sessions = {}
            if os.path.exists(f"{server}.json"):
                with open(f'{server}.json', 'r') as cache_file:
                    cache = json.load(cache_file)
            self.__get_departments(server)
            processes = [m.Process(target=self._auth_worker, args=(server, cache)) for _ in range(24)]
            for p in processes:
                p.start()
            self.__input_queue.join()
            while True:
                try:
                    item = self.__output_queue.get(timeout=1)
                    sessions.update(item)
                except Empty:
                    break
            print(f"Sessions: {len(sessions)}")
            with open(f'{server}.json', 'w') as cache_file:
                cache_file.write(json.dumps(sessions))
            for p in processes:
                p.join()
            self.__sessions.update(sessions)

    def __get_departments(self, server):
        server += '.example.com'
        res = requests.get(f"https://{server}/fastlogin/login.php", allow_redirects=True)
        html = fromstring(res.text)
        departments = html.xpath('//select[@id="location"]')[0].getchildren()
        print(f"departments: {len(departments)}")
        for department in departments:
            self.__input_queue.put(department.attrib['value'])

    def _auth_worker(self, server, cache):
        while True:
            try:
                department = self.__input_queue.get(timeout=2)
                element = f"{server}:{department}"
                if (
                        element in cache
                        and not cache[element]['Student'] == ''
                        and not cache[element]['Teacher'] == ''
                ):
                    self.__output_queue.put({element: cache[element]})
                else:
                    item = {
                        element: {
                            'Student': self.__auth('Student01', 'science', department, server),
                            'Teacher': self.__auth('Teacher01', 'science', department, server)
                        }
                    }
                    self.__output_queue.put(item)
                    print(f"ITEM sent: {element}")
                self.__input_queue.task_done()
            except Empty:
                print(f"exiting process {os.getpid()}, ppid: {os.getppid()}")
                break

    def __auth(self, user, password, location, server):
        server += '.example.com'
        with requests.Session() as session:
            res = session.get(f"https://{server}/fastlogin/login.php")
            html = fromstring(res.text)
            csrf_token = html.forms[0].inputs['_csrf_token'].value
            session.post(
                f"https://{server}/fastlogin/login_check.php",
                data={
                    '_username': user,
                    '_password': password,
                    '_location': location,
                    '_submit': 'Login',
                    '_csrf_token': csrf_token
                },
                allow_redirects=True,
            )
            auth_token = '='.join(session.cookies.items()[1])
        return auth_token

    def __prepare_data(self):
        for i in range(len(self.__input)):
            self.__input[i][3] = int(self.packets_per_role_department / 100 * self.__input[i][2])
        for code, session in self.__sessions.items():
            for num, scenario in enumerate(self.__input):
                for i in range(scenario[3]):
                    self.__result.append({
                        'session': session[scenario[0]],
                        'link': scenario[1],
                        'index': f"{num}-{code}",
                    })
        shuffle(self.__result)

    def __add_ammo_to_file(self, ammo_obj, file_name):
        with open(file_name, 'a') as file:
            file.write(ammo_obj.format())


if __name__ == '__main__':
    AmmoAlitest().run()
