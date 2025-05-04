This is a simple stopwatch class. Example:

```py
from tados_stopwatch import Stopwatch
import time

s = Stopwatch()

s.start()
time.sleep(3)
print(s.get())

time.sleep(2)
s.stop()
print(s.get())

s.reset()

s.set(14)

s.bind(3, lambda: print("3 seconds have passed"))

while s.get() < 5:
    print("Updated")
    time.sleep(1)
```