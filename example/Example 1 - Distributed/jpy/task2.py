import time
from jpy import app
@app.task(ignore_result=True)
def multiply(x, y):
    print('multiply')
    return x * y