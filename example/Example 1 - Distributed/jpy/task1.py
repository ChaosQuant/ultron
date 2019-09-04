import time
from jpy import app
@app.task(ignore_result=True)
def add(x, y):
    print('add')
    return x + y