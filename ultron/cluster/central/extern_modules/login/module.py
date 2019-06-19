# -*- coding: utf-8 -*-
import pdb
import datetime
import json
from ultron.cluster.central.extern_modules.base_module import BaseModule
from ultron.cluster.central.extern_modules.middleware.module import ModelsSingleton
class Module(BaseModule):
    def __init__(self, name, redis_client):
        super(Module, self).__init__(name, redis_client)
        self._func = {'login_in':self.login_in,
                     'heart_tick':self.heart_tick}
        
    
    def process_respone(self, result):
        name = result['name']
        opcode = result['opcode']
        self._func[opcode](result)
    
    def login_in(self, result):
        wid = result['wid']
        login_info = {'name':'login','opcode':'login_info','result':'sucess'}
        queue_name = 'ultron:work:work_id:' + wid
        work_info = {'wid':wid,'token':result['token'],
                     'queue_name':queue_name,
                    'login_time':result['login_time'],
                    'update_time':datetime.datetime.now()}
        print(wid,result,queue_name)
        ModelsSingleton().add_cluster(wid, work_info)
        self._redis_client.hset(queue_name, wid, json.dumps(login_info))
     
    def heart_tick(self, result):
        ModelsSingleton().set_alive(result['wid'])