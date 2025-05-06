import collections.abc


def mapping_update_r(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = mapping_update_r(d.get(k, {}), v)
        else:
            d[k] = v
    return d
