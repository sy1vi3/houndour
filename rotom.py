import requests, base64, time
from typing import List, Dict

class Rotom:
    __slots__ = ['__rotom_url', '__http_user', '__http_pass', '__session', '__config', '__devices']
    
    def __init__(self, config: dict) -> None:
        self.__rotom_url = config['rotom_url'] + '/api/status'
        self.__http_user = config['rotom_user']
        self.__http_pass = config['rotom_pass']
        self.__session = requests.Session()
        self.__session.headers.update({'Authorization': Rotom.basic_auth(self.__http_user, self.__http_pass)})
        self.__config = config
        self.__devices: Dict[dict] = config['devices']
        for device in self.__devices:
            self.__devices[device]['isAlive'] = True
            self.__devices[device]['deathCount'] = 0
            self.__devices[device]['needsReboot'] = False
            self.__devices[device]['lastRebootedTime'] = time.time()
            self.__devices[device]['deviceName'] = device

    @staticmethod
    def basic_auth(username: str, password: str) -> str:
        return f'Basic {base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")}'
    
    @staticmethod
    def data_list_to_dict(data: List[dict]) -> dict:
        devices_dict = dict()
        for device in data:
            devices_dict[device['deviceId']] = device
        return devices_dict
    
    def get_status_page(self):
        try:
            data = Rotom.data_list_to_dict(self.__session.get(self.__rotom_url).json()['devices'])
            for device in self.__devices:
                if device in data:
                    isAlive = data[device]['isAlive']
                    self.__devices[device]['isAlive'] = isAlive
                    if isAlive:
                        self.__devices[device]['deathCount'] = 0
                        self.__devices[device]['needsReboot'] = False
                    else:
                        self.__devices[device]['deathCount'] += 1
                        if self.__devices[device]['deathCount'] >= self.get_timeout_limit():
                            self.__devices[device]['needsReboot'] = True
                        else:
                            self.__devices[device]['needsReboot'] = False
                else:
                    self.__devices[device]['isAlive'] = False
                    self.__devices[device]['needsReboot'] = True
        except Exception as e:
            print(e)

    def get_reboot_needed(self) -> List[dict]:
        needs_reboot = list()
        for device in self.__devices:
            if self.__devices[device]['needsReboot'] == True and time.time() - self.__devices[device]['lastRebootedTime'] > 120:
                needs_reboot.append(self.__devices[device])
                self.__devices[device]['lastRebootedTime'] = time.time()
        return needs_reboot
    
    def get_check_interval(self) -> int:
        return self.__config['check_interval']
    
    def get_timeout_limit(self) -> int:
        return self.__config['timeout_limit']
    
    def get_startup_script(self) -> str:
        return self.__config['startup_script_path']

    