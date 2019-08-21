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
        self._func = {'startup_task':self.startup_task,
                     'shutoff_task':self.shutoff_task,
                     'restart_task':self.restart_task,
                     'update_task':self.update_task}
        
    
    def process_respone(self, result):
        name = result['name']
        opcode = result['opcode']
        self._func[opcode](result)
    
    def update_task(self, result):
        second_time = time.time()
        task_id = int(second_time * 1000000 + datetime.datetime.now().microsecond)
        wid = result['wid']
        #获取消息通道
        queue = ModelsSingleton().get_queue(wid)
        self._redis_client.hset(queue, str(task_id),json.dumps(result))
                      
    def startup_task(self, result):
        second_time = time.time()
        task_id = int(second_time * 1000000 + datetime.datetime.now().microsecond)
        work_name = result['work_name']
        dir_name = result['dir_name']
        task_info = {'name':'tasks','opcode':'startup_task','work_name':work_name,
                    'dir_name':dir_name}
        queue_list = ModelsSingleton().get_all_queue()
        for queue in queue_list:
            self._redis_client.hset(queue,str(task_id),json.dumps(task_info))
    
    def shutoff_task(self, result):
        second_time = time.time()
        task_id = int(second_time * 1000000 + datetime.datetime.now().microsecond)
        work_name = result['work_name']
        dir_name = result['dir_name']
        task_info = {'name':'tasks','opcode':'shutoff_task','work_name':work_name,
                    'dir_name':dir_name}
        queue_list = ModelsSingleton().get_all_queue()
        for queue in queue_list:
            self._redis_client.hset(queue,str(task_id),json.dumps(task_info))
        
    def restart_task(self, result):
        second_time = time.time()
        task_id = int(second_time * 1000000 + datetime.datetime.now().microsecond)
        work_name = result['work_name']
        dir_name = result['dir_name']
        task_info = {'name':'tasks','opcode':'restart_task','work_name':work_name,
                    'dir_name':dir_name}
        queue_list = ModelsSingleton().get_all_queue()
        for queue in queue_list:
            self._redis_client.hset(queue,str(task_id),json.dumps(task_info))