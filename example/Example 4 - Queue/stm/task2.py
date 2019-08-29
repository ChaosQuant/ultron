import time
from . import app
@app.task(ignore_result=True)
def multiply(x, y):
    time.sleep(2)
    return x * y