from toolz import keyfilter


def pick(whitelist, d):
    return keyfilter(lambda k: k in whitelist, d)
