from typing import ValuesView
from uuid import uuid4

from compiler import decorators

@decorators.service
class EchoBackend(object):
    def __init__(self):
        pass

    def req(self, value: int):
        return value