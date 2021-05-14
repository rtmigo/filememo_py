# [filememo](https://github.com/rtmigo/filememo_py#readme)

File-based **memoization** decorator. Stores the results of expensive function calls and returns the cached result 
when the same inputs occur again.

CI-tested with Python 3.8-3.9 on macOS, Ubuntu and Windows.

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

When you specify `version`, all results with different version values 
are deprecated.


``` python3
@memoize(version=1)
def function(a, b):
    return a + b
```

For example, you changed your mind and now the function should return the 
product of numbers instead of the sum. But the cache already contains 
the previous results with the sums. In this case, you can just change
`version`. Previous results will not be returned.

``` python3
@memoize(version=2)
def function(a, b):
    return a * b
```

Keep in mind that the version value is common to the entire directory.

Do **not** use different version with the same directory. This will lead to a messy deletion of data from the cache.

``` python3
@memoize(dir_path='/my/cache/', version=2)  # BAD: version conflict
def that_function(a, b):
    pass
    
@memoize(dir_path='/my/cache/', version=3)  # BAD: version conflict 
def other_function(a, b):
    pass
```

But if the directories are different, then there is no problem.

``` python3
@memoize(dir_path='/my/cache/that', version=2)  # OK
def that_function(a, b):
    pass
    
@memoize(dir_path='/my/cache/other', version=3)  # OK 
def other_function(a, b):
    pass
```

If the directory is not specified, then there are no problems either: the 
results of different functions are automatically saved in different directories.

``` python3
@memoize(version=2)  # OK
def that_function(a, b):
    pass
    
@memoize(version=3)  # OK 
def other_function(a, b):
    pass
```