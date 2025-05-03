```python3
import threading
import time
from terminate_thread import terminate, kill


def thread_func1():
    n = 0
    while True:
        n += 1
        print(n, t)
        time.sleep(1)


if __name__ == "__main__":
    t = threading.Thread(target=thread_func1, )
    t.start()
    time.sleep(2)

    terminate(t)
    # or
    kill(t)

    exit(0)


```
