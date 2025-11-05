"""
Advanced Decorator Pattern with Extendable Methods

This example demonstrates a decorator pattern where:
1. A metaclass marks methods as "extendable"
2. BaseDecorator provides empty implementations for all extendable methods
3. Child decorators override only the methods they want to extend
4. When an extendable method is called, the decorator's method is automatically called after
"""


def extendable(func):
    """Decorator to mark a method as extendable"""
    func._extendable = True
    return func


class ExtendableMeta(type):
    """
    Metaclass that identifies extendable methods and wraps them to call
    decorator methods after execution.
    """
    def __new__(mcs, name, bases, namespace):
        extendable_methods = []

        # Find all methods marked as extendable
        for key, value in list(namespace.items()):
            if callable(value) and hasattr(value, '_extendable'):
                extendable_methods.append(key)
                original_method = value

                # Create wrapper that calls decorator methods after execution
                def make_wrapper(method_name, original):
                    def wrapper(self, *args, **kwargs):
                        # Execute the original method
                        result = original(self, *args, **kwargs)

                        # Call the corresponding method on all attached decorators
                        if hasattr(self, '_decorators') and self._decorators:
                            for decorator in self._decorators:
                                decorator_method = getattr(decorator, method_name, None)
                                if decorator_method and callable(decorator_method):
                                    # Call decorator method with same arguments
                                    decorator_method(*args, **kwargs)

                        return result

                    wrapper.__name__ = original.__name__
                    wrapper.__doc__ = original.__doc__
                    return wrapper

                namespace[key] = make_wrapper(key, original_method)

        # Create the class
        cls = super().__new__(mcs, name, bases, namespace)

        # Store the list of extendable methods on the class
        cls._extendable_methods = extendable_methods

        return cls


class BaseDecorator:
    """
    Base decorator class that dynamically creates stub methods for all
    extendable methods from the decorated component.
    """
    def __init__(self, component):
        self.component = component

        # Initialize decorators list on component if not exists
        if not hasattr(component, '_decorators'):
            component._decorators = []

        # Register this decorator with the component
        component._decorators.append(self)

        # Dynamically create stub methods for all extendable methods
        if hasattr(component.__class__, '_extendable_methods'):
            for method_name in component.__class__._extendable_methods:
                # Only create stub if child class hasn't overridden it
                if not self._has_overridden_method(method_name):
                    self._create_stub_method(method_name)

    def _has_overridden_method(self, method_name):
        """Check if child class has overridden this method"""
        # Get the method from the instance's class
        method = getattr(self.__class__, method_name, None)
        # If it exists and is not from BaseDecorator, it's overridden
        if method is not None:
            return method_name not in BaseDecorator.__dict__
        return False

    def _create_stub_method(self, method_name):
        """Create a no-op stub method"""
        def stub(*args, **kwargs):
            pass  # Empty implementation

        stub.__name__ = method_name
        setattr(self, method_name, stub)


# ============================================================================
# Example Usage
# ============================================================================

class Coffee(metaclass=ExtendableMeta):
    """Base coffee class with extendable methods"""

    def __init__(self):
        self.cost = 2.0
        self.description = "Simple coffee"

    @extendable
    def prepare(self):
        print(f"Preparing {self.description}")

    @extendable
    def serve(self):
        print(f"Serving {self.description} (${self.cost:.2f})")

    @extendable
    def cleanup(self):
        print("Cleaning up coffee machine")

    def get_cost(self):
        """Non-extendable method"""
        return self.cost


class MilkDecorator(BaseDecorator):
    """Decorator that adds milk to coffee - overrides prepare and serve"""

    def prepare(self):
        print("  + Adding steamed milk")
        self.component.cost += 0.5
        self.component.description += " with milk"

    def serve(self):
        print("  + Topping with milk foam")


class SugarDecorator(BaseDecorator):
    """Decorator that adds sugar - only overrides prepare"""

    def prepare(self):
        print("  + Adding sugar")
        self.component.cost += 0.3
        self.component.description += " and sugar"


class LoggingDecorator(BaseDecorator):
    """Decorator that logs all operations - overrides all methods"""

    def prepare(self):
        print("  [LOG] Preparation step completed")

    def serve(self):
        print("  [LOG] Serving step completed")

    def cleanup(self):
        print("  [LOG] Cleanup step completed")


if __name__ == "__main__":
    print("=" * 60)
    print("Example 1: Simple Coffee (no decorators)")
    print("=" * 60)
    coffee1 = Coffee()
    coffee1.prepare()
    coffee1.serve()
    coffee1.cleanup()
    print()

    print("=" * 60)
    print("Example 2: Coffee with Milk")
    print("=" * 60)
    coffee2 = Coffee()
    MilkDecorator(coffee2)
    coffee2.prepare()
    coffee2.serve()
    coffee2.cleanup()
    print()

    print("=" * 60)
    print("Example 3: Coffee with Milk and Sugar")
    print("=" * 60)
    coffee3 = Coffee()
    MilkDecorator(coffee3)
    SugarDecorator(coffee3)
    coffee3.prepare()
    coffee3.serve()
    coffee3.cleanup()
    print()

    print("=" * 60)
    print("Example 4: Coffee with Milk, Sugar, and Logging")
    print("=" * 60)
    coffee4 = Coffee()
    MilkDecorator(coffee4)
    SugarDecorator(coffee4)
    LoggingDecorator(coffee4)
    coffee4.prepare()
    coffee4.serve()
    coffee4.cleanup()
    print()

    print(f"Final cost: ${coffee4.get_cost():.2f}")
