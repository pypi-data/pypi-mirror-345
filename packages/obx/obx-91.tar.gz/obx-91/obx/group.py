# This file is placed in the Public Domain.


"collections"


import time


class Group:

    def add(self, obj):
        self.__dict__[time.time()] = obj

    def all(self):
        return self.__dict__.values()


def __dir__():
    return (
        "Group",
    )
