
##
## This is a class that does all logging locally (replacing Beldi)
##
## TODO: Move the following comment to the Logger superclass
##
## It currently implements a full API with all methods, but in the future,
## it would make sense to have it be agnostic to the actual API calls (invocation, store, etc)
##

from runtime import serde

from runtime.local import invoke

## TODO: Make a Logger abstraction, that contains everything that the store abstraction does
from runtime.store_abstraction import Store

class LocalLogger(Store):
    ## TODO: @haoran It is not clear whether the name is supposed to be given at:
    ##       1. initialization/__init__ (called by deployment/context) 
    ##       2. init_env (called by the compiled service)
    ##       Also it is not clear if the Beldi initialization should also happen in (1) or (2)
    def __init__(self):
        pass
        # self.store = beldi_stub.Beldi()

    ## This method initializes the environment,
    ##   which is essential to invoke store methods.
    ##
    ## In the stub context it is not actually important.
    def init_env(self, name="default-store"):
        ## TODO: We can remove the env, since it is not needed by the local
        ##       logger.
        self.env = None
        self.name = name
        self.store = {}

    ## TODO: Modify the compiler to call the loggers init_clients.

    def init_clients(self, clients={}):
        self.clients = clients

    ## TODO: Modify the compiler to call SyncInvoke, etc in Logger

    ## TODO: Test all of these changes in the remote one too.

    ## This implements a read method on the store
    ##
    ## Normally, this would also use the environment
    ## to perform the invocation
    def eos_read(self, key):
        try:
            serialized_val = self.store[key]
            return serde.deserialize(serialized_val)
        except:
            return None
    
    ## This implements a write method on the store
    ##
    ## Normally, this would also use the environment
    ## to perform the invocation
    def eos_write(self, key, value):
        self.store[key] = serde.serialize(value)
    
    ## TODO: These are still empty and their APIs undecided.
    ##
    ## TODO: We need to implement them for Beldi
    def contains(self, key):
        return key in self.store
        
    def set_if_not_exists(self, key, value):
        self.begin_tx()
        if (not self.contains(key)):
            self.eos_write(key, value)
        self.end_tx()

    def begin_tx(self):
        pass

    def end_tx(self):
        pass        

    ##
    ## Invocations
    ##
    def SyncInvoke(self, client_name: str, method_name: str, *args):
        client = self.clients[client_name]
        return invoke.SyncInvoke(client, method_name, *args)

    def AsyncInvoke(self, client_name: str, method_name: str, *args):
        client = self.clients[client_name]
        return invoke.AsyncInvoke(client, method_name, *args)

    def Wait(self, promise):
        return invoke.Wait(promise)

    def WaitAll(self, *promises):
        return invoke.WaitAll(*promises)