

## Synchronous local invocation.
## Simply find the method in the client and call it.
def SyncInvoke(client, method_name: str, *args):
    return getattr(client, method_name)(*args)

## All promises must implement a wait method
class Promise:
    def __init__(self):
        pass

    def wait(self):
        raise NotImplementedError()

## Poor local promises :')
class MethodCallPromise(Promise):
    def __init__(self, method, *args):
        self.method = method
        self.args = args

    def wait(self):
        return self.method(*(self.args))


def AsyncInvoke(client, method_name: str, *args) -> Promise:
    return MethodCallPromise(getattr(client, method_name), *args)

def Wait(promise: Promise):
    assert(isinstance(promise, Promise))
    return promise.wait()

def WaitAll(*promises):
    responses = []
    for promise in promises:
        assert(isinstance(promise, Promise))
        responses.append(promise.wait())
    return responses