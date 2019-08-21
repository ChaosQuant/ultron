import time
from celery import Celery
app = Celery('tasks', broker='redis://:12345678dx@47.95.193.202:6378/0')

@app.task
def send_mail(email):
    print('sending email %s' %(email))
    import time
    return "success"
