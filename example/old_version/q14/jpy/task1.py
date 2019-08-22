import time
from jpy import app
@app.task(ignore_result=True)
def add(x, y):
    time.sleep(2)
    return x + y