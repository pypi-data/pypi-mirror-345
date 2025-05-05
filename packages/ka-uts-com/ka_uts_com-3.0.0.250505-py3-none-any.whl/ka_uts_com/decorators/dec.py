"""
Decorators
"""
# coding=utf-8
from ka_uts_com.timer import Timer


def timer(fnc):
    def wrapper(*args, **kwargs):
        Timer.start(fnc)
        fnc(*args, **kwargs)
        Timer.end(fnc)
    return wrapper
