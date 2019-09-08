from functools import partial
from toolz import keyfilter, compose, reduceby, merge, excepts
from pymysql.err import ProgrammingError


def pick(whitelist, d):
    return keyfilter(lambda k: k in whitelist, d)


def sum_by(key):
    return compose(sum, partial(map, lambda x: x.get(key)))


def key_by(key, items):
    return reduceby(key, lambda a, x: merge(a, x), items, {})


split_to_list = excepts(
    AttributeError,
    compose(
        partial(filter, lambda x: x),
        partial(map, lambda x: x.strip()),
        lambda x: x.split(","),
    ),
    lambda x: None,
)


def with_report_error_check(data_fn):
    def fn(*args, **kwargs):
        try:
            return data_fn(*args, **kwargs)
        except ProgrammingError:
            return []

    return fn


map_resolved = compose(list, map)
