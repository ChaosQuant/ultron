# -*- coding: utf-8 -*-
import datetime
import json
import socket
from ultron.cluster.work.extern_modules.base_module import BaseModule

class Module(BaseModule):
    def __init__(self, name, wid, token, redis_client):
        super(Module, self).__init__(name, wid, token ,redis_client)
        self._func = {'login_info':self.login_info,
                     'heart_tick':self.heart_tick}
        self._namespace = 'login'
        self._is_logined = 0

    def login_master(self):
        #若登录成功，则通过WID对应的消息队列发送消息
        login_info = {'name':self._namespace,
                      'opcode':'login_in',
                      'wid':self._wid, 'token':self._token,
                      'ip': socket.gethostbyname(socket.getfqdn(socket.gethostname())),
                      'login_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%S:%M")}
        self._redis_client.hset('ultron:work:login', self._wid + login_info['opcode'], json.dumps(login_info))
    
    def heart_tick(self, respone):
        if self._is_logined == 0 or self._wid is None or self._token is None:
            return
        heart_info = {'name': self._namespace,
                     'opcode': 'heart_tick',
                     'wid':self._wid, 'token':self._token,
                     'update_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%S:%M")}
        self._redis_client.hset('ultron:work:login', self._wid + heart_info['opcode'], json.dumps(heart_info))
        
    def process_respone(self, respone):
        name = respone['name']
        opcode = respone['opcode']
        self._func[opcode](respone)
      
    def login_info(self, respone):
        result = respone['result']
        self._is_logined = 1
        print(result)
        
        