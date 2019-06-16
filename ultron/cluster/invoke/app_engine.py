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
        else:
            self._host = config.redis_host
            self._port = config.redis_port
            self._pwd = config.redis_pwd
            
    def create_engine(self, task_name):
        redis_url = 'redis://:' + self._pwd + '@' + self._host + ':' + str(self._port) + '/1'
        app = Celery(task_name, broker=redis_url,
                    backend=redis_url)
        self._app = app
        return self._app
    
    def async_result(self):
        asynct = AsyncResult(id="ed88fa52-11ea-4873-b883-b6e0f00f3ef3", app=self._app)
        if asynct.successful():
            result = asynct.get()
            print(result)
            # result.forget() # 将结果删除
        elif asynct.failed():
            print('执行失败')
        elif asynct.status == 'PENDING':
            print('任务等待中被执行')
        elif asynct.status == 'RETRY':
            print('任务异常后正在重试')
        elif asynct.status == 'STARTED':
            print('任务已经开始被执行')

        
        
 
create_app = AppEngine().create_engine
async_result = AppEngine().async_result