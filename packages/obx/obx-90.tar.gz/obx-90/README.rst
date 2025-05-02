OBX
===


**NAME**


``OBX`` - objects


**SYNOPSIS**


::

    >>> from obx import Object, read, write
    >>> o = Object()
    >>> oo = Object()
    >>> o.a = "b"
    >>> pth = write(o)
    >>> read(oo, pth)
    'store/obx.object.Object/2025-04-15/13:53:24.685981'
    >>> print(oo)
    {'a': 'b'}
    >>>


**DESCRIPTION**


``OBX`` allows for easy json save//load to/from disk of objects. It
provides an "clean namespace" Object class that only has dunder
methods, so the namespace is not cluttered with method names. This
makes storing and reading to/from json possible.


**INSTALL**


installation is done with pip

|
| ``$ pip install obx``
|


**AUTHOR**

|
| ``Bart Thate`` <``bthate@dds.nl``>
|

**COPYRIGHT**

|
| ``OBX`` is Public Domain.
|
