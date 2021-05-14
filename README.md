# [filememo](https://github.com/rtmigo/filememo_py#readme)

Permanently caches previous function results.

Based on [pickledir](https://github.com/rtmigo/pickledir_py#readme).

# Use

``` python3
from filememo import memoize

@memoize
def long_running_function(a, b, c):
    return compute()

# the following line actually computes the value only
# when the program runs for the first time. On subsequent 
# runs, the value is simply read from the file
x = long_running_function(1, 2, 3)
```

## Arguments

Results of different functions with different arguments are stored 
separately.

``` python3
@memoize
def other_function(a, b):
    return compute()

# the following calls will cache three different values 
y1 = long_running_function(1, 2, 3)  
y2 = long_running_function(3, 2, 4)
y3 = other_function(1, 2)

# the way the arguments are set is also important, as is their order. 
# Therefore, the following calls are cached as three different ones
y4 = other_function(1, b=2)
y5 = other_function(a=1, b=2)
y6 = other_function(b=2, a=1)
```

## Directory

All data is saved in a temporary directory. All data is saved in a temporary 
directory. You can specify which one.

``` python3
@memoize(dir_path='/var/tmp/myfuncs')
def function(a, b):
    return compute()
```

## Expiration date

``` python3
@memoize(max_age = datetime.timedelta(minutes=5))
def function(a, b):
    return compute()
```

## Data version

This parameter is the same as `version` in [pickledir](https://github.com/rtmigo/pickledir_py#readme).


``` python3
@memoize(version=1)
def function(a, b):
    return compute()
```
