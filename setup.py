from pathlib import Path

from setuptools import setup


def load_module_dict(filename: str) -> dict:
    import importlib.util as ilu
    filename = Path(__file__).parent / filename
    spec = ilu.spec_from_file_location('', filename)
    module = ilu.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.__dict__


name = "filememo"

setup(
    name=name,
    version=load_module_dict(f'{name}/_constants.py')['__version__'],
    author="Artёm IG",
    author_email="ortemeo@gmail.com",
    url='https://github.com/rtmigo/filememo_py#readme',

    python_requires='>=3.8',  # needed by pickledir
    install_requires=['pickledir>=0.3.5'],
    packages=[name],

    description="File-based memoization decorator. Stores the results of "
                "expensive function calls and returns the cached result "
                "when the same inputs occur again.",

    keywords="python package memoize memoization cache function file "
             "persistent method memoize-decorator "
             "memoization-library permanent pickle".split(),

    long_description=(Path(__file__).parent / 'README.md').read_text(),
    long_description_content_type='text/markdown',

    license='MIT',

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        # python 3.8 is required by pickledir
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
    ],
)
