"""
Simple Decorator Pattern using Metaprogramming

This example demonstrates a basic decorator pattern enhanced with metaclasses
to automatically apply decorators to methods.
"""


# Basic function decorator
def log_calls(func):
    """Simple decorator that logs function calls"""
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Finished {func.__name__}")
        return result
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


# Metaclass for automatic decorator application
class DecoratorMeta(type):
    """
    Metaclass that automatically applies decorators to methods
    based on naming convention or explicit registration.
    """
    def __new__(mcs, name, bases, namespace):
        # Apply log_calls decorator to all methods starting with 'do_'
        for key, value in namespace.items():
            if callable(value) and key.startswith('do_'):
                namespace[key] = log_calls(value)

        return super().__new__(mcs, name, bases, namespace)


# Example class using the metaclass
class Worker(metaclass=DecoratorMeta):
    """Example worker class with decorated methods"""

    def __init__(self, name):
        self.name = name

    def do_work(self):
        """This method will be automatically decorated"""
        print(f"{self.name} is working...")
        return "Work completed"

    def do_task(self, task):
        """This method will also be automatically decorated"""
        print(f"{self.name} is performing task: {task}")
        return f"Task '{task}' completed"

    def status(self):
        """This method won't be decorated (doesn't start with 'do_')"""
        print(f"{self.name} status check")
        return "OK"


# Class decorator for adding functionality
def add_timestamp(cls):
    """Class decorator that adds timestamp functionality to a class"""
    original_init = cls.__init__

    def new_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        from datetime import datetime
        self.created_at = datetime.now()

    cls.__init__ = new_init

    def get_age(self):
        from datetime import datetime
        return (datetime.now() - self.created_at).total_seconds()

    cls.get_age = get_age
    return cls


@add_timestamp
class TimedWorker(Worker):
    """Worker with timestamp tracking"""
    pass


if __name__ == "__main__":
    print("=" * 50)
    print("Basic Worker Example")
    print("=" * 50)

    worker = Worker("Alice")

    # These methods are automatically decorated by the metaclass
    worker.do_work()
    print()
    worker.do_task("Build system")
    print()

    # This method is not decorated
    worker.status()
    print()

    print("=" * 50)
    print("Timed Worker Example")
    print("=" * 50)

    timed_worker = TimedWorker("Bob")
    timed_worker.do_work()
    print()

    import time
    time.sleep(1)
    print(f"Worker created {timed_worker.get_age():.1f} seconds ago")
