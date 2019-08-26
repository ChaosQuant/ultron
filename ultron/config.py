# -*- coding: utf-8 -*-
import pdb
import six
import json 
import os
import shutil
from ultron.utilities.singleton import Singleton
from ultron.setting import setting_info, file_name

@six.add_metaclass(Singleton)
class ConfigSingletion(object):
    def __init__(self):
        __str__ = 'ConfigSingletion'
        self.queue_host = ''
        self.queue_port = 0
        self.queue_pwd = ''
        self.queue_user = ''
        self.queue_db = 0
        self.queue_type = ''
        self._init_setting()
        
    def _init_setting(self):
        l = json.loads(setting_info)
        for setting in l:
            values = l[setting]
            if setting == 'queue':
                self._init_queue(setting, values)
    
    def _init_queue(self, key, kwargs):
        self.set_queue(kwargs)
            
    def set_queue(self, kwargs):
        self.queue_type = kwargs['type']
        if self.queue_type == 'redis':
            self.queue_host = kwargs['host']
            self.queue_port = kwargs['port']
            self.queue_pwd = kwargs['pwd']
            self.queue_db = kwargs['db'] if 'db' in kwargs else 0
        elif self.queue_type == 'amqp':
            self.queue_host = kwargs['host']
            self.queue_port = kwargs['port']
            self.queue_user = kwargs['user']
            self.queue_pwd = kwargs['pwd']
            self.queue_db = kwargs['db'] if 'db' in kwargs else 0
            
    def update(self):
        self._save_setting()
        
    def save_queue(self):
        kwargs = {}
        kwargs['type'] = self.queue_type
        kwargs['host'] = self.queue_host
        kwargs['port'] = self.queue_port
        kwargs['user'] = self.queue_user
        kwargs['pwd'] = self.queue_pwd
        kwargs['db'] = self.queue_db
        return kwargs
        
            
    def _save_setting(self):
        kwargs = {}
        kwargs['queue'] = self.save_queue()
        info_str = json.dumps(kwargs)
        content = "import os\nsetting_info='{0}'\nfile_name = os.path.join(os.getcwd(), __file__)".format(info_str)
        #卸载引用库
        pyc_path = str(file_name.split('.')[0]) + '.pyc'
        if os.path.exists(pyc_path):
            os.remove(pyc_path)
        if os.path.exists(file_name):
            os.remove(file_name)
        with open(file_name, 'wb') as f:
            f.write(bytes(content,encoding='utf8'))
        
config_setting = ConfigSingletion()