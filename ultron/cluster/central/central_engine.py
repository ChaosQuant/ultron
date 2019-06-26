# -*- coding: utf-8 -*-
import pdb
import json
import gevent
import importlib
from gevent.queue import Queue
from ultron.utilities.redis.redis_client import RedisClient
from ultron.cluster.central.extern_modules.modules_info import moddules_info
from ultron.config import config_setting

LOGIN_QUEUE = 'ultron:work:login'
CTASK_QUEUE = 'ultron:work:ctask' #获取启动TASK指令通道
UPDATE_QUEUE = 'ultron:work:update' #同步代码文件

class CentralEngine(object):
    def __init__(self, **kwargs):
        self._module_dict = {}
        self._redis_client = RedisClient(host=config_setting.queue_host,
                                          port=config_setting.queue_port,
                                          password=config_setting.queue_pwd)
        self._queue_list = [LOGIN_QUEUE,CTASK_QUEUE,UPDATE_QUEUE]
        self._task_queue = Queue() #
        self.init_modules()
        gevent.spawn(self._get_task)
        gevent.spawn(self._dispatch_task)
        gevent.sleep()

    def init_modules(self):
        l = json.loads(moddules_info)
        for setting in l:
            self.load_modules(setting)

    def load_modules(self, setting):
        name = setting['name']
        is_effective = setting['isEffective']
        if is_effective == 0:
            return
        module_name = 'ultron.cluster.central.extern_modules.' + name + '.module'
        try:
            module = importlib.import_module(module_name)
            if 'Module' in dir(module):
                strategy_class = module.__getattribute__('Module')
                self._module_dict[name] = strategy_class(name,self._redis_client)
        except Exception as e:
            print('Failed to import module: %s:[%s]' % (name,str(e))) 
    
    def _get_task(self):
        while True:
            for queue in self._queue_list:
                task_all = self._redis_client.hmgetall(queue)
                task_list = task_all[0]
                self._redis_client.hmdel(queue, task_list.keys())
                for tid, task in task_list.items():
                    self._task_queue.put(json.loads(task))
            gevent.sleep(.3)

    def _dispatch_task(self):
        while True:
            while not self._task_queue.empty():
                task = self._task_queue.get()
                space_name = str(task.get('name'))
                if space_name in self._module_dict:
                    self._module_dict[space_name].process_respone(task)
            gevent.sleep(.3)