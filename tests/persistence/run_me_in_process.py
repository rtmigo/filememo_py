import sys
from pathlib import Path
from filememo import memoize

cache_path = Path(__file__).parent / "temp" / "cachedir"


def increase_value_in_file(basename: str):
    file = (Path(__file__).parent / "temp" / basename)
    file.parent.mkdir(exist_ok=True)
    try:
        t = file.read_text()
    except FileNotFoundError:
        t = '0'

    file.write_text(str(int(t) + 1))


@memoize(dir_path=cache_path)
def cached():
    increase_value_in_file('_memoized.txt')


def non_cached():
    increase_value_in_file('_non_memoized.txt')


@memoize(version=sys.argv[2] if len(sys.argv) >= 3 else None)
def cached_systemp():
    increase_value_in_file('_memoized_systemp.txt')


if __name__ == "__main__":
    if sys.argv[1] == "memoized":
        cached()
    elif sys.argv[1] == "non_memoized":
        non_cached()
    elif sys.argv[1] == "systemp":
        cached_systemp()

    else:
        raise ValueError
