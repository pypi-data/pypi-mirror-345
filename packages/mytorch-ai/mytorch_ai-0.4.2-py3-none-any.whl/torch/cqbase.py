import functools
import threading

class CQBase():
    _id_counter = 0
    local_data = threading.local()  # Thread-local storage

    def __init__(self):
        self._instance_id = self._generate_unique_id()

    @classmethod
    def _generate_unique_id(cls):
        with threading.Lock():
            cls._id_counter += 1
            return f"instance_{cls._id_counter}"

    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        # Intercept callable attributes (methods) and wrap them with decorator
        if callable(attr) and not name.startswith('_'):
            @functools.wraps(attr)
            def intercepted_method(*args, **kwargs):
                #print(f"CLIENT: Intercepted {name} with args={args}, kwargs={kwargs}")
                # Check if the method is being called from a super() call
                if getattr(self.local_data, '_in_super_call', False):
                    # Check if the intercepted method exists on the proxy
                    if hasattr(self.proxy, name):
                        # Call the method remotely using the proxy
                        result = getattr(self.proxy, name)(*args, **kwargs)
                        print(f"SERVER RESULT: {result}")
                        return result
                    else:
                        print(f"CLIENT: {name} not found on server")
                # If not in a super() call, execute the original method locally
                return attr(*args, **kwargs)
            return intercepted_method
        return attr
    
    def __del__(self):
        self.proxy.delete()
        pass