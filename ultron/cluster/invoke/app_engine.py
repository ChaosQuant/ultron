from celery import Celery
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
        else:
            self._host = config.redis_host
            self._port = config.redis_port
            self._pwd = config.redis_pwd
            
    def create_engine(self, task_name):
        redis_url = 'redis://:' + self._pwd + '@' + self._host + ':' + str(self._port) + '/0'
        app = Celery(task_name, broker='redis://:12345678dx@47.95.193.202:6378/0')
        return app
 
create_app = AppEngine().create_engine