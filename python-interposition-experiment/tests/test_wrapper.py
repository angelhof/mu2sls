import logging

from runtime import wrappers, beldi_stub, serde

# logging.basicConfig(level=logging.DEBUG)

class Counter:
    def __init__(self):
        self.value = 0

    def get(self):
        return self.value
    
    def set(self, value):
        self.value = value

    def increment(self):
        self.value += 1


        

def test_list():

    ## This Descriptor Class will be generated by the compiler
    class WrapperCollection:
        def __get__(self, obj, objtype=None):
            value = obj._wrapper_collection
            logging.info('Accessing collection')
            return value

        def __set__(self, obj, value):
            logging.info('Setting collection')
            # print('Setting collection', obj.beldi.get('test-collection'), 'with value:',  value)
            if(isinstance(value, wrappers.WrapperTerminal)):
                obj._wrapper_collection = value
            else:
                logging.info('Collection %r with value: %r', serde.deserialize(obj.beldi.get('test-collection')), value)
                obj._wrapper_collection._wrapper_set(value)

    class TestObject:
        collection = WrapperCollection()
        def __init__(self):

            ## Initialize a beldi_stub instance
            self.beldi = beldi_stub.Beldi()

            ## TODO: What is the correct key for a persistent object? It might be one per service? So maybe we should use the service name?
            collection_key = "test-collection"
            collection_init_val = []
            self.collection = wrappers.wrap_terminal(collection_key, collection_init_val, self.beldi)

            # print(dir(collection))
            
            # print(wrapped_collection.__repr__())
            # print(dir(wrapped_collection))

            self.collection.append(0)

            assert self.collection.index(0) == 0

            self.collection.append(1)
            assert self.collection.index(0) == 0
            assert self.collection.index(1) == 1

            el = self.collection.pop()
            assert el == 1
            assert self.collection.index(0) == 0

            el = self.collection.pop()
            assert el == 0

            assert self.collection + [5] == [5]

            self.collection = [1]
            assert self.collection.index(1) == 0

            self.collection += [5]
            assert self.collection.index(1) == 0
            assert self.collection.index(5) == 1

            el = self.collection.pop()
            assert el == 5
    ## We need a TestObject to check descriptors (since all execution will happen in a service anyway).    
    _ = TestObject()

def test_counter():

    counter_key = "test-counter"

    ## This Descriptor Class will be generated by the compiler
    class WrapperCounter:
        def __get__(self, obj, objtype=None):
            value = obj._wrapper_counter
            logging.info('Accessing counter')
            return value

        def __set__(self, obj, value):
            logging.info('Setting counter')
            if(isinstance(value, wrappers.WrapperTerminal)):
                obj._wrapper_counter = value
            else:
                logging.info('counter %r with value: %r', serde.deserialize(obj.beldi.get(counter_key)), value)
                obj._wrapper_counter._wrapper_set(value)

    class TestObject:
        counter = WrapperCounter()
        def __init__(self):
            beldi = beldi_stub.Beldi()

            ## TODO: What is the correct key for a persistent object? It might be one per service? So maybe we should use the service name?
            
            counter_init_val = Counter()
            counter = wrappers.wrap_terminal(counter_key, counter_init_val, beldi)

            assert counter.value == 0
            assert counter.get() == 0

            counter.increment()

            assert counter.value == 1
            assert counter.get() == 1

            counter.set(5)

            assert counter.value == 5
            assert counter.get() == 5

            counter.value = 4

            assert counter.value == 4
            assert counter.get() == 4

            counter = Counter()
            assert counter.value == 0

    _ = TestObject()

## TODO: For this test to pass, we need to wrap integers (and other primitives differently)
def test_int_counter():
    counter_key = "test-int-counter"

    ## This Descriptor Class will be generated by the compiler
    class WrapperCounter:
        def __get__(self, obj, objtype=None):
            value = obj._wrapper_counter
            logging.info('Accessing counter')
            return value

        def __set__(self, obj, value):
            logging.info('Setting counter')
            if(isinstance(value, wrappers.WrapperTerminal)):
                obj._wrapper_counter = value
            else:
                logging.info('counter %r with value: %r', serde.deserialize(obj.beldi.get(counter_key)), value)
                obj._wrapper_counter._wrapper_set(value)

    class TestObject:
        counter = WrapperCounter()
        def __init__(self):
            beldi = beldi_stub.Beldi()

            ## TODO: What is the correct key for a persistent object? It might be one per service? So maybe we should use the service name?
            counter_init_val = 0
            counter = wrappers.wrap_terminal(counter_key, counter_init_val, beldi)

            # print(counter + 1)
            
            assert counter == 0
            assert counter == 0

            counter += 1

            assert counter == 1
            assert counter == 1

            counter = 5

            assert counter == 5
            assert counter == 5

            counter = 4

            assert counter == 4
            assert counter == 4
    
    _ = TestObject()
