## RapidQ
![License](https://img.shields.io/badge/license-BSD3-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10_%7c_3.11_%7c_3.12_%7c_3.13-blue)
[![PyPI Version](https://img.shields.io/pypi/v/RapidQ?style=flat-square?cacheSeconds=3600)](https://pypi.org/project/RapidQ/)
![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)
<!-- ![Views](https://komarev.com/ghpvc/?username=rapidq&label=Repo+Views) -->
<!-- [![Download Stats](https://img.shields.io/pypi/dm/rapidq)](https://pypistats.org/packages/rapidq) -->
#### For those who want a bare minimum task queue, Just run and discard, no headaches.
#### Only &#x1F90F; ~700 lines of code
A lightweight &#x1FAB6; and fast &#x1F680; background task processing library for Python, developed with simplicity in mind.<br>
There is nothing fancy, no gimmick, RapidQ is a simple and easy to use package - works on any OS (yes, it supports windows).<br>
Only Redis broker is currently available, and there is no result backend(could be implemented later).<br>

Inspired by `celery` and `dramatiq`, but lightweight, and easy to use for small projects.<br>

### Installation
```
pip install rapidq
```

#### It has: <br>
   - Only Redis as broker, with json and pickle serialization options.
   - Process based workers, and is faster
   - No result backend
   - No retry behavior (of course it will be added)
   - No monitoring, as of now.

#### It requires: <br>
   - No configurations for local setup. Although some broker property can be configured.

----------
### Motivation
Simply put - I just wanted to see if I could do it.  <br>
This was part of my hobby project that somehow became a package &#x1F917;<br>
Understanding how packages like `celery` and `dramatiq` works internally was a challenge I faced. I wanted a package that is understandable and simple.<br>

----------
### _This project is under development, so expect breaking changes when you upgrade_

----------
### A working example

The below code is available in `example\minimal.py`
```python
# my_task.py
from rapidq import RapidQ

app = RapidQ()

@app.background_task(name="simple-task")
def test_func(msg):
    # of course this function could do more than just print.
    print("simple task is running")
    print(msg)


if __name__ == "__main__":
    test_func.in_background(msg="Hello, I'm running in background")
     # Line below will be printed directly and will not go to worker.
    test_func(msg="Hello, I'm running in the same process!")
```
Copy paste the above into a python file, say `my_task.py`<br>

Run the rapidq worker first. <br>`rapidq my_task` <br>

Then on another terminal, run the my_task.py <br> `python my_task.py`

----------
### Customizing broker properties
If you wish to customize the serialization to use pickle (json by default) or want to change the broker url?<br>
It can be customized with a small configuration, using a simple python file. Checkout this file ->`example\config_example.py`.<br>
I used a python module because you can run any arbitrary code to read config from any other options such as .env .
check similar example in `example\minimal_custom.py` and `example\config_example.py`
```python
# my_custom_task.py
from rapidq import RapidQ

app = RapidQ()

# define the custom configuration. Below line can be omitted if configuration is not needed.
app.config_from_module("example.config_example")


@app.background_task(name="simple-task")
def test_func(msg):
    print("simple task is running")
    print(msg)


if __name__ == "__main__":
    test_func.in_background(msg="Hello, I'm running")
```

You can run `rapidq` as before. <br>`rapidq my_custom_task` <br>
Then on another terminal, run the my_custom_task.py <br> `python my_custom_task.py`

----------
### Number of workers.
By default RapidQ uses 4 worker processes or the number of CPUs available on your system, whichever is smaller.
You can control the number of workers by passing -w argument.  Eg `rapidq my_task -w 6`. Which will start 6 worker processes.

----------
### Flushing broker
May be you tested a lot and flooded your broker with messages.<br>
You can flush the broker by running `rapidq-flush`

### Integrating with web frameworks
It can be easily integrated with Flask and FastAPI applications. A simple Flask and FastAPI example is in **example** directory.
Currently RapidQ cannot be easily integrated with Django. Django support is coming in next version.

### Local development
For local development in windows, you can use either of the following ways to get Redis working.
1) Redis for windows from: https://github.com/redis-windows/redis-windows
2) Using redis with WSL: https://redis.io/docs/latest/operate/oss_and_stack/install/archive/install-redis/install-redis-on-windows/
3) Using a remote Redis server.

----------
