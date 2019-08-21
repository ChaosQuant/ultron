# -*- coding: utf-8 -*-
import pdb
import datetime
import time
import json
from ultron.cluster.central.extern_modules.base_module import BaseModule
from ultron.cluster.central.extern_modules.middleware.module import ModelsSingleton

class Module(BaseModule):
    def __init__(self, name, redis_client):
        super(Module, self).__init__(name, redis_client)
        self._func = {'upload_packet':self.upload_packet}
     
    def process_respone(self, result):
        name = result['name']
        opcode = result['opcode']
        self._func[opcode](result)
    
    def upload_packet(self, result):
        second_time = time.time()
        task_id = int(second_time * 1000000 + datetime.datetime.now().microsecond)
        queue_list = ModelsSingleton().get_all_queue()
        for queue in queue_list:
            self._redis_client.hset(queue,str(task_id),json.dumps(result))