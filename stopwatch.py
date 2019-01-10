'''Wrapper for timing functions and function for 
making time strings human readable.
'''

__all__ = ['formatted_time', 'timer']
__version__ = '1.0'
__author__ = 'Richard Skogeby'

from time import time, sleep


def formatted_time(t):
    r_n = 3
    if t <= 1e-3:
        t = t * 1e6
        t_string = ''.join([str(round(t,r_n)),' us'])
        return t_string 
    if t <= 1e-0:
        t = t * 1e3
        t_string = ''.join([str(round(t,r_n)),' ms'])
        return t_string
    if t <= 999:
        t = t * 1e0
        t_string = ''.join([str(round(t,r_n)),' s'])
        return t_string
    else:
        return ''.join([str(t),' s'])


def timer(function):
    def f(*args, **kwargs):
        before = time()
        print('Running', function.__name__, '. . .', end='\r')
        rv = function(*args, **kwargs)
        after = time()
        t = after - before
        print(function.__name__, 'executed in', formatted_time(t))
        return rv
    return f
