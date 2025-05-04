# This file is placed in the Public Domain.


__doc__ = __name__.upper()


from .disk   import getpath, ident, read, write
from .object import Object, construct, fqn, items, keys, values, update
from .json   import dumps, loads


__all__ = (
    'Object',
    'construct',
    'dumps',
    'ident',
    'items',
    'keys',
    'loads',
    'read',
    'values',
    'update',
    'write'
)


def __dir__():
    return __all__
