# [filememo](https://github.com/rtmigo/filememo_py#readme)

File-based **memoization** decorator. Caches the results of expensive function
calls. Retains the cached results between program restarts.

CI tests are done in Python 3.8, 3.9 and 3.10 on macOS, Ubuntu and
Windows.

---

The function can be *expensive* because it is slow, or uses a lot of system
resources, or literally makes a request to a paid API.

The `memoize` decorator returns the cached result when the same function called
with the same arguments. Thus, the function is expensive only once and
inexpensive thereafter.

For example, the simplest cache for downloaded data can be set like this:

``` python3
@memoize
def downloaded(url):
    return requests.get(url)
    
downloaded("http://example.net/aaa")  # downloads data
downloaded("http://example.net/bbb")  # downloads data
downloaded("http://example.net/aaa")  # gets data from cache   
```

Data is saved to the file system using
[pickledir](https://pypi.org/project/pickledir/). Even after the program
restart, the cached results will be in place.

``` python3
# gets data from cache after restart
downloaded("http://example.net/aaa")     
```

# Install

``` bash
$ pip3 install filememo
```

# Use

``` python3
from filememo import memoize

@memoize
def long_running_function(a, b, c):
    return compute()

# the following line actually computes the value only
# when the program runs for the first time. On subsequent 
# runs, the value is read from the file
x = long_running_function(1, 2, 3)
```

## Function arguments

The results depend on both the function and its arguments. All results are
cached separately.

``` python3
@memoize
def that_function(a, b, c):
    return compute(a, b, c)

@memoize
def other_function(a, b):
    return compute(a, b)

# the following calls will cache three different values 
y1 = that_function(1, 2, 3)  
y2 = that_function(30, 20, 40)
y3 = other_function(1, 2)

# the way the arguments are set is also important, as is their order. 
# Therefore, the following calls are cached as three different ones
y4 = other_function(1, b=2)
y5 = other_function(a=1, b=2)
y6 = other_function(b=2, a=1)
```

## Cache directory

If `dir_path` is not specified, the cached data is stored in the directory
returned by
the [`gettempdir`](https://docs.python.org/3/library/tempfile.html#tempfile.gettempdir)
. However, there is a high probability that the cache stored there will not
survive a reboot. And even a certain probability that the system does not have a
temporary directory, so the current directory will be considered temporary.

To better control the situation, you can set a specific directory for storing
caches.

``` python3
@memoize(dir_path='/var/tmp/myfuncs')
def function(a, b):
    return a+b
    
# it's ok if different functions share the same directory    
@memoize(dir_path='/var/tmp/myfuncs')
def other_func():
    return compute()
```

## Expiration date

The `max_age` argument sets two conditions at once:

- if the result is not yet in the cache (and we will add it now), then it will
  live in the cache no longer than `max_age`. After that it will be
  automatically deleted
- if the result is already in the cache, then we only use it if its age is less
  than `max_age`. Otherwise, the function will be run again, and the result will
  be replaced with a new one

``` python3
@memoize(max_age = datetime.timedelta(minutes=5))
def function(a, b):
    return compute()
```

## Data version

When you specify `version`, all results with different versions are considered
outdated.

Say you have the following function:

``` python3
@memoize(version=1)
def function(a, b):
    return a + b
```

You changed your mind, and now the function should return the product of numbers
instead of the sum. But the cache already contains the previous results with the
sums. In this case, you can just change
`version`. Previous results will not be returned.

``` python3
@memoize(version=2)
def function(a, b):
    return a * b
```

Note that all **other** than the current version are deprecated, regardless of
whether their value is greater or less. If you used `version=10`, and then
started using `version=9`, then 9 is considered current, and 10 is obsolete.

## Exceptions

If the decorated function throws an exception, the error is considered
permanent. The exception is stored in the cache and will be raised every time.

``` python3
from filememo import memoize, FunctionException

@memoize
def divide(a, b):
    return a / b

try:
    # tryng to run the function for the first time
    divide(1, 0)
except FunctionException as e:
    print(f"Error: {e.inner}")      

try:
    # not actually running again, getting error from cache
    divide(1, 0)
except FunctionException as e:
    print(f"Cached error: {e.inner}")      
```

The `exceptions_max_age = None` argument will prevent exceptions from being
cached. Each error will be considered a one-time error.

``` python3
@memoize(exceptions_max_age = None)
def download(url):
    return http_get(url)
    
while True:
    try:
        download('http://sample.net/path')
        break
    except FunctionException:
        time.sleep(1)
        # will retry        
```

You can also set the expiration time for cached exceptions. It may differ from
the caching time of the data itself.

``` python3
# keep downloaded data for a day, remember connection errors for 5 minutes

@memoize(max_age = datetime.timedelta(days: 1)
         exceptions_max_age = datetime.timedelta(minutes: 5))
def download(url):
    return http_get(url)
```

## In-memory caching

Each call to a function decorated with `@memoize` results in I/O operations. If
your absolute priority is performance, then even reading from the disk cache can
be considered expensive. Although `filememo` does not attempt to cache the read
data in memory, this functionality is easy to achieve by combining decorators.

``` python3
from functools import lru_cache
from filememo import memoize

@lru_cache
@memoize
def too_expensive():
    return compute()
```

In this example, the `filememo` disk cache will be used to store the results
between program runs, while the `functools` RAM cache will store the results
between function calls.

If the data is already in disk cache, and the program is just started, then
calling `too_expensive()` for the first time will read the result from disk.
Further calls to `too_expensive()` will return the result from memory.