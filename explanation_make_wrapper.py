"""
Detailed Explanation of make_wrapper and Decorator Registration

This file explains the timing and mechanics of how the extendable decorator pattern works.
"""

# Let's trace through the execution timeline:

print("=" * 70)
print("TIMELINE OF EVENTS")
print("=" * 70)

# ============================================================================
# PHASE 1: CLASS CREATION TIME (when Python interprets the class definition)
# ============================================================================

print("\n1. CLASS CREATION TIME - Metaclass runs")
print("-" * 70)

def extendable(func):
    """Marks a method as extendable"""
    func._extendable = True
    return func


class ExtendableMeta(type):
    """
    The metaclass runs when the class is DEFINED, not when instances are created.
    """
    def __new__(mcs, name, bases, namespace):
        print(f"   → Metaclass creating class '{name}'")

        extendable_methods = []

        for key, value in list(namespace.items()):
            if callable(value) and hasattr(value, '_extendable'):
                extendable_methods.append(key)
                original_method = value

                # This is where make_wrapper is called
                def make_wrapper(method_name, original):
                    """
                    IMPORTANT: make_wrapper creates a closure.

                    Why do we need this function?
                    - We need to capture 'method_name' and 'original' for each method
                    - Without this closure, all wrappers would share the same variables
                      from the loop (closure over loop variable problem)
                    """
                    def wrapper(self, *args, **kwargs):
                        """
                        This wrapper is created at CLASS CREATION time,
                        but it EXECUTES at RUNTIME (when method is called).

                        Key insight: The wrapper doesn't need to know what decorators
                        exist at creation time. It checks for them at RUNTIME.
                        """
                        print(f"      [wrapper] Executing original method: {method_name}")
                        result = original(self, *args, **kwargs)

                        # CHECK AT RUNTIME: Does this instance have decorators?
                        print(f"      [wrapper] Checking for decorators on instance...")
                        if hasattr(self, '_decorators') and self._decorators:
                            print(f"      [wrapper] Found {len(self._decorators)} decorator(s)")
                            for i, decorator in enumerate(self._decorators):
                                decorator_method = getattr(decorator, method_name, None)
                                if decorator_method and callable(decorator_method):
                                    print(f"      [wrapper] Calling decorator #{i+1}.{method_name}()")
                                    decorator_method(*args, **kwargs)
                        else:
                            print(f"      [wrapper] No decorators found")

                        return result

                    wrapper.__name__ = original.__name__
                    return wrapper

                # Replace the original method with the wrapped version
                print(f"   → Wrapping method: {key}")
                namespace[key] = make_wrapper(key, original_method)

        cls = super().__new__(mcs, name, bases, namespace)
        cls._extendable_methods = extendable_methods
        print(f"   → Class '{name}' created with extendable methods: {extendable_methods}")
        return cls


# When this class is defined, the metaclass runs
class Coffee(metaclass=ExtendableMeta):
    """The metaclass runs NOW, as soon as this class is defined"""

    def __init__(self):
        self.name = "Coffee"
        # Note: _decorators is NOT created here - it will be created by BaseDecorator

    @extendable
    def prepare(self):
        print(f"         [{self.name}] Preparing coffee...")


# ============================================================================
# PHASE 2: DECORATOR CLASS CREATION
# ============================================================================

print("\n2. DECORATOR CLASSES DEFINED")
print("-" * 70)

class BaseDecorator:
    """
    BaseDecorator is responsible for:
    1. Registering itself with the component
    2. Creating stub methods
    """
    def __init__(self, component):
        print(f"   → BaseDecorator.__init__ called for {self.__class__.__name__}")
        self.component = component

        # THIS IS WHERE _decorators GETS CREATED AND POPULATED!
        if not hasattr(component, '_decorators'):
            print(f"   → Creating _decorators list on component")
            component._decorators = []

        # Register this decorator instance with the component
        print(f"   → Registering {self.__class__.__name__} with component")
        component._decorators.append(self)
        print(f"   → Component now has {len(component._decorators)} decorator(s)")

        # Create stub methods for extendable methods not overridden
        if hasattr(component.__class__, '_extendable_methods'):
            for method_name in component.__class__._extendable_methods:
                if not self._has_overridden_method(method_name):
                    self._create_stub_method(method_name)

    def _has_overridden_method(self, method_name):
        method = getattr(self.__class__, method_name, None)
        if method is not None:
            return method_name not in BaseDecorator.__dict__
        return False

    def _create_stub_method(self, method_name):
        def stub(*args, **kwargs):
            pass
        stub.__name__ = method_name
        setattr(self, method_name, stub)


class MilkDecorator(BaseDecorator):
    """This decorator overrides prepare"""
    def prepare(self):
        print(f"         [MilkDecorator] Adding milk...")


class SugarDecorator(BaseDecorator):
    """This decorator also overrides prepare"""
    def prepare(self):
        print(f"         [SugarDecorator] Adding sugar...")


# ============================================================================
# PHASE 3: RUNTIME - Creating instances and calling methods
# ============================================================================

print("\n3. RUNTIME - Creating instances and attaching decorators")
print("-" * 70)

print("\nCreating coffee instance:")
coffee = Coffee()
print(f"   → coffee._decorators exists? {hasattr(coffee, '_decorators')}")

print("\nAttaching MilkDecorator:")
milk = MilkDecorator(coffee)

print("\nAttaching SugarDecorator:")
sugar = SugarDecorator(coffee)

print(f"\n   → coffee._decorators = {coffee._decorators}")
print(f"   → List contents: {[d.__class__.__name__ for d in coffee._decorators]}")

print("\n4. CALLING coffee.prepare()")
print("-" * 70)
print("\n   Calling coffee.prepare()...\n")
result = coffee.prepare()

print("\n" + "=" * 70)
print("KEY INSIGHTS")
print("=" * 70)
print("""
1. make_wrapper creates the wrapper at CLASS CREATION time
   - It doesn't know about decorators yet
   - It doesn't need to know!

2. The wrapper checks for _decorators at RUNTIME (when method is called)
   - By then, BaseDecorator instances may have populated the list
   - The wrapper is generic - it works with any number of decorators

3. _decorators list gets populated when:
   - BaseDecorator.__init__ is called
   - Each decorator instance adds itself to the component's _decorators list

4. This is late binding:
   - The wrapper is created early (class definition)
   - But it looks up decorators late (method call time)
   - You can even add/remove decorators after the instance is created!

5. Why make_wrapper is needed:
   - Without it, all wrappers would share the same loop variables
   - The closure captures method_name and original for each specific method
""")

print("\n" + "=" * 70)
print("DEMONSTRATING DYNAMIC DECORATOR ADDITION")
print("=" * 70)

class VanillaDecorator(BaseDecorator):
    def prepare(self):
        print(f"         [VanillaDecorator] Adding vanilla...")

print("\nAdding another decorator AFTER previous calls:")
vanilla = VanillaDecorator(coffee)

print("\nCalling coffee.prepare() again with 3 decorators:\n")
coffee.prepare()
