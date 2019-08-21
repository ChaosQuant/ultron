from q13_app import task1
from a13_app import task2
import time

print(task1.add.delay(2, 8).get())
print('add')
print(task2.multiply.delay(3, 7).get())
print('delay')