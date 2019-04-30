from functools import partial
from toolz import keyfilter, compose, reduceby, merge


def pick(whitelist, d):
    return keyfilter(lambda k: k in whitelist, d)


def sum_by(key):
    return compose(sum, partial(map, lambda x: x.get(key)))


def key_by(key, items):
    return reduceby(key, lambda a, x: merge(a, x), items, {})
