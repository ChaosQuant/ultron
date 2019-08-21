# -*- coding: utf-8 -*-
import pdb
import json
import datetime
import gevent
import importlib
import hashlib
from gevent.queue import Queue
from ultron.utilities.redis.redis_client import RedisClient
from ultron.cluster.work.extern_modules.modules_info import moddules_info
from ultron.utilities.short_uuid import unique_machine
from ultron.config import config_setting


class WorkEngine(object):
    def __init__(self, **kwargs):
        self._module_dict = {}
        self._redis_client = RedisClient(host=config_setting.queue_host,
                                          port=config_setting.queue_port,
                                          password=config_setting.queue_pwd)
        self._secret_key = 'd6f89b09'
        self._wid = unique_machine
        self._queue_list = ['ultron:work:work_id:'+str(self._wid)]
        #生成token
        self._token = hashlib.sha1((self._secret_key + self._wid.replace('-','')).encode()).hexdigest()
        self._task_queue = Queue() #
        self.init_modules()
        gevent.spawn(self._get_task)
        gevent.spawn(self._dispatch_task)
        gevent.spawn(self._heart_tick)
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
        module_name = 'ultron.cluster.work.extern_modules.' + name + '.module'
        try:
            module = importlib.import_module(module_name)
            if 'Module' in dir(module):
                strategy_class = module.__getattribute__('Module')
                self._module_dict[name] = strategy_class(name,self._wid, self._token, self._redis_client)
                print('module %s loading' % (name))
                if name == 'login':
                    self._module_dict[name].login_master()
        except Exception as e:
            print('Failed to import module:%s:[%s]' % (name,str(e)))
    
    def _heart_tick(self):
        last_time = datetime.datetime.now()
        while True:
            now_time = datetime.datetime.now()
            if (now_time - last_time).seconds > 20: #发送心跳包
                task = {'name':'login','opcode':'heart_tick'}
                self._module_dict[task['name']].process_respone(task)
                last_time = now_time
            gevent.sleep(.3)
            
    def _get_task(self):
        while True:
            for queue in self._queue_list:
                task_all = self._redis_client.hmgetall(queue)
                task_list = task_all[0]
                self._redis_client.hmdel(queue, task_list.keys())
                for tid, task in task_list.items():
                    self._task_queue.put(json.loads(task))
            gevent.sleep(.3)
            
    #用于处理各个节点登录
    def _dispatch_task(self):
        while True:
            while not self._task_queue.empty():
                task = self._task_queue.get()
                space_name = str(task.get('name'))
                if space_name in self._module_dict:
                    self._module_dict[space_name].process_respone(task)
            gevent.sleep(.3)
