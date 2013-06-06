

class IgnoreException:
    def __init__(self, exc_type=Exception):
        self.exc_type = exc_type

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            return

        return issubclass(exc_type, self.exc_type)
