def singleton(cls):
    instances = {}

    class SingletonWrapper(cls):
        def __new__(inner_cls, *args, **kwargs):
            if cls not in instances:
                instances[cls] = super(SingletonWrapper, inner_cls).__new__(inner_cls, *args, **kwargs)
                instances[cls]._initialized = False  # Initialize the flag
            return instances[cls]

        def __init__(self, *args, **kwargs):
            if not self._initialized:
                super(SingletonWrapper, self).__init__(*args, **kwargs)
                self._initialized = True  # Mark as initialized

        @classmethod
        def reset_instance(inner_cls):
            if cls in instances:
                del instances[cls]

    SingletonWrapper.__name__ = cls.__name__
    SingletonWrapper.__module__ = cls.__module__
    return SingletonWrapper
