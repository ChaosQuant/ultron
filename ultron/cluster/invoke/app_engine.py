from celery import Celery
from celery.result import AsyncResult
from celery.schedules import crontab
import six
from ultron.utilities.singleton import Singleton
import ultron.config as config

@six.add_metaclass(Singleton)
class AppEngine(object):
    def __init__(self, **kwargs):
        if ('host'  in kwargs) and ('port'  in kwargs) and ('pwd'  in kwargs):
            self._host = kwargs['host']
            self._port = kwargs['port']
            self._port = kwargs['pwd']
            self._db = kwargs['db']
        else:
            self._host = config.redis_host
            self._port = config.redis_port
            self._pwd = config.redis_pwd
            self._db = config.redis_db
            
    def create_engine(self, task_name, module_list = []):
        redis_url = 'redis://:' + self._pwd + '@' + self._host + ':' + str(self._port) + '/' + str(self._db)
        app = Celery(task_name, broker=redis_url,
                    backend=redis_url)
        class Config:
            CELERY_TIMEZONE = 'Asia/Shanghai'
            if len(module_list) > 0:
                CELERY_IMPORTS = tuple(module_list)
        app.config_from_object(Config)
        return app
        

        
        
 
create_app = AppEngine().create_engine
