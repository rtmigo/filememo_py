# [filememo](https://github.com/rtmigo/filememo_py#readme)

Permanently caches previous function results.

Based on [pickledir](https://github.com/rtmigo/pickledir_py#readme).

``` python3
from filememo import memoize

@memoize
def long_running_function(a, b, c):
  ...
```
