from stm.task1 import add
from stm.task2 import multiply

tm = add.delay(4,2)
tm.ready()
print(tm.get())
tp = multiply.delay(6,2)
print(tp.get())