from celery import Celery

app = Celery('stm',
             #broker='redis://:12345678dx@127.0.0.1:6379/1',
             #backend='redis://:12345678dx@127.0.0.1:6379/1',
             broker='pyamqp://ultron:123456dx@127.0.0.1:5672/ultron',
             backend='amqp://',
             include=['stm.task1', 'stm.task2'])  # 配置文件和任务文件分开了，可以写多个任务文件

# app 扩展配置
app.conf.update(
    result_expires=3600,
)