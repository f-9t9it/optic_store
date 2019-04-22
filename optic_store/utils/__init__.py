from functools import partial
from toolz import keyfilter, compose


def pick(whitelist, d):
    return keyfilter(lambda k: k in whitelist, d)


def sum_by(key):
    return compose(sum, partial(map, lambda x: x.get(key)))
