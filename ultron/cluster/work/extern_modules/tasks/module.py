# -*- coding: utf-8 -*-
import pdb
import datetime
import json
import subprocess
from ultron.cluster.work.extern_modules.base_module import BaseModule

class Module(BaseModule):
    def __init__(self, name, wid, token, redis_client):
        super(Module, self).__init__(name, wid, token, redis_client)
        self._func = {'startup_task':self.startup_task,
                     'shutoff_task':self.shutoff_task,
                     'restart_task':self.restart_task,
                     'update_task': self.update_task}
        self._namespace = 'tasks'
        
    def process_respone(self, respone):
        name = respone['name']
        opcode = respone['opcode']
        self._func[opcode](respone)
    
    def update_task(self, respone):
        dir_name = respone['dir_name']
        tasks = respone['tasks']
        for task in tasks:
            dir_line = 'cd ' + dir_name
            stop_line = 'ps auxww | grep \'active- (-A  '+ str(task) + ' worker\' | awk \'{print $2}\' | xargs kill -9'
            subprocess.Popen(stop_line, shell=True)
            celery_line = 'celery -A ' + task + ' worker --loglevel=info'
            command_line = dir_line + ' && ' + celery_line
            subprocess.Popen(command_line, shell=True)
        
    def startup_task(self, respone):
        work_name = respone['work_name']
        dir_name = respone['dir_name']
        #celery -A polymeriza worker --loglevel=info
        dir_line = 'cd ' + dir_name
        stop_line = 'ps auxww | grep \'active- (-A  '+ str(work_name) + ' worker\' | awk \'{print $2}\' | xargs kill -9'
        celery_line = 'celery -A ' + work_name + ' worker --loglevel=info -E'
        command_line = dir_line + ' && ' + celery_line
        subprocess.Popen(command_line, shell=True)
    
    def shutoff_task(self, respone):
        work_name = respone['work_name']
        dir_name = respone['dir_name']
        command_line = 'ps auxww | grep \'active- (-A  '+ str(work_name) + ' worker\' | awk \'{print $2}\' | xargs kill -9'
        subprocess.Popen(command_line, shell=True)
    
    def restart_task(self):
        work_name = respone['work_name']
        dir_name = respone['dir_name']
        dir_line = 'cd ' + dir_name
        kill_line = 'ps auxww | grep \'active- (-A  '+ str(work_name) + ' worker\' | awk \'{print $2}\' | xargs kill -9'
        start_line = 'celery -A ' + work_name + ' worker --loglevel=info'
        command_line = dir_line + ' && ' + kill_line + ' && ' + start_line
        subprocess.Popen(command_line, shell=True)
        

    