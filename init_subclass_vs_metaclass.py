"""
__init_subclass__ vs Metaclass: When to Use Which?

This example demonstrates the differences between __init_subclass__ and metaclasses,
showing use cases where each is more appropriate.
"""


# ============================================================================
# Use Case 1: Plugin Registry - Both Work, __init_subclass__ is Simpler
# ============================================================================

print("=" * 70)
print("Use Case 1: Plugin Registry")
print("=" * 70)

# Approach A: Using __init_subclass__ (SIMPLER)
print("\nApproach A: Using __init_subclass__")


class PluginBase:
    """Simple plugin registry using __init_subclass__"""
    _registry = {}

    def __init_subclass__(cls, plugin_name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        name = plugin_name or cls.__name__
        cls._registry[name] = cls
        print(f"  Registered: {name}")


class PluginA(PluginBase, plugin_name="A"):
    pass


class PluginB(PluginBase, plugin_name="B"):
    pass


print(f"Registered plugins: {list(PluginBase._registry.keys())}")


# Approach B: Using Metaclass (MORE COMPLEX, unnecessary for this case)
print("\nApproach B: Using Metaclass (overkill for this case)")


class PluginMeta(type):
    """Metaclass for plugin registry"""
    _registry = {}

    def __new__(mcs, name, bases, namespace, plugin_name=None, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace)
        if name != 'PluginBaseMeta':  # Skip the base class itself
            pname = plugin_name or name
            mcs._registry[pname] = cls
            print(f"  Registered: {pname}")
        return cls


class PluginBaseMeta(metaclass=PluginMeta):
    pass


class PluginC(PluginBaseMeta, plugin_name="C"):
    pass


class PluginD(PluginBaseMeta, plugin_name="D"):
    pass


print(f"Registered plugins: {list(PluginMeta._registry.keys())}")

print("\n✓ Winner: __init_subclass__ - Much simpler for this use case!")


# ============================================================================
# Use Case 2: Method Call Interception - Metaclass is REQUIRED
# ============================================================================

print("\n" + "=" * 70)
print("Use Case 2: Method Call Interception")
print("=" * 70)

# __init_subclass__ CANNOT intercept method calls at runtime
# It only runs during class creation

# Metaclass CAN intercept method calls via __call__
print("\nUsing Metaclass (only option for this)")


class SingletonMeta(type):
    """
    Metaclass that implements singleton pattern.
    __init_subclass__ cannot do this because we need to intercept
    instance creation (__call__).
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Intercept instance creation"""
        if cls not in cls._instances:
            print(f"  Creating first instance of {cls.__name__}")
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        else:
            print(f"  Returning existing instance of {cls.__name__}")
        return cls._instances[cls]


class Database(metaclass=SingletonMeta):
    def __init__(self, name):
        self.name = name


db1 = Database("main")
db2 = Database("other")  # Will return the same instance
print(f"db1 is db2: {db1 is db2}")
print(f"Database name: {db1.name}")

print("\n✓ Winner: Metaclass - __init_subclass__ cannot intercept instance creation!")


# ============================================================================
# Use Case 3: Attribute Access Control - Metaclass with __getattribute__
# ============================================================================

print("\n" + "=" * 70)
print("Use Case 3: Attribute Access Control")
print("=" * 70)

print("\nUsing Metaclass (only option for class-level attribute control)")


class RestrictedMeta(type):
    """
    Metaclass that restricts what class attributes can be set.
    __init_subclass__ cannot do this - it only runs once at class creation.
    """
    def __setattr__(cls, name, value):
        if name.startswith('_forbidden_'):
            raise AttributeError(f"Cannot set attribute '{name}'")
        super().__setattr__(name, value)


class RestrictedClass(metaclass=RestrictedMeta):
    allowed_attr = "OK"


print("  Setting allowed_attr: ", end="")
RestrictedClass.allowed_attr = "Modified"
print("Success!")

print("  Setting _forbidden_attr: ", end="")
try:
    RestrictedClass._forbidden_attr = "Not allowed"
except AttributeError as e:
    print(f"Error! {e}")

print("\n✓ Winner: Metaclass - __init_subclass__ cannot control attribute access!")


# ============================================================================
# Use Case 4: Automatic Method Decoration - Both Work
# ============================================================================

print("\n" + "=" * 70)
print("Use Case 4: Automatic Method Decoration")
print("=" * 70)

# Both approaches work, but __init_subclass__ is clearer


def log_call(func):
    def wrapper(*args, **kwargs):
        print(f"    Calling {func.__name__}")
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


print("\nApproach A: Using __init_subclass__")


class LoggedBase:
    """Automatically log methods starting with 'action_'"""
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for name, method in cls.__dict__.items():
            if callable(method) and name.startswith('action_'):
                setattr(cls, name, log_call(method))


class MyService(LoggedBase):
    def action_process(self):
        return "Processing"

    def helper(self):
        return "Helper"


service = MyService()
print("  action_process() - decorated:")
service.action_process()
print("  helper() - not decorated:")
service.helper()


print("\nApproach B: Using Metaclass")


class LoggedMeta(type):
    """Automatically log methods starting with 'action_'"""
    def __new__(mcs, name, bases, namespace):
        for key, value in list(namespace.items()):
            if callable(value) and key.startswith('action_'):
                namespace[key] = log_call(value)
        return super().__new__(mcs, name, bases, namespace)


class MyService2(metaclass=LoggedMeta):
    def action_process(self):
        return "Processing"

    def helper(self):
        return "Helper"


service2 = MyService2()
print("  action_process() - decorated:")
service2.action_process()
print("  helper() - not decorated:")
service2.helper()

print("\n✓ Winner: __init_subclass__ - More readable and easier to understand!")


# ============================================================================
# Use Case 5: Customizing Class Creation with Parameters
# ============================================================================

print("\n" + "=" * 70)
print("Use Case 5: Customizing Class Creation with Parameters")
print("=" * 70)

print("\nUsing __init_subclass__ with parameters")


class ConfigurableBase:
    """Base class that accepts configuration parameters"""
    def __init_subclass__(cls, tablename=None, readonly=False, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.tablename = tablename or cls.__name__.lower()
        cls.readonly = readonly
        print(f"  {cls.__name__}: table={cls.tablename}, readonly={cls.readonly}")


class Users(ConfigurableBase, tablename="users_table"):
    pass


class Settings(ConfigurableBase, tablename="app_settings", readonly=True):
    pass


class Products(ConfigurableBase):  # Uses default tablename
    pass


print("\n✓ __init_subclass__ makes parameterized inheritance very clean!")


# ============================================================================
# Summary and Decision Guide
# ============================================================================

print("\n" + "=" * 70)
print("DECISION GUIDE")
print("=" * 70)

summary = """
Use __init_subclass__ when you need to:
✓ Register subclasses (plugin systems)
✓ Validate class attributes at creation time
✓ Automatically decorate methods when class is defined
✓ Add class attributes based on parameters
✓ Enforce that subclasses implement certain attributes/methods
✓ Configure subclasses with keyword arguments

Use Metaclass when you need to:
✓ Control instance creation (e.g., Singleton pattern)
✓ Intercept attribute access on the class itself
✓ Customize how the class behaves as an object
✓ Implement complex class-level behavior
✓ Control the creation of the class object itself
✓ Implement ORM-like behavior with complex descriptors

Key Differences:

┌─────────────────────┬──────────────────────┬────────────────────────┐
│ Feature             │ __init_subclass__    │ Metaclass              │
├─────────────────────┼──────────────────────┼────────────────────────┤
│ Timing              │ After class creation │ During class creation  │
│ Scope               │ Subclass creation    │ Class + instance       │
│ Complexity          │ Simple               │ More complex           │
│ Inheritance         │ Natural              │ Can be tricky          │
│ Parameters          │ Via keyword args     │ Via __new__ args       │
│ Instance control    │ No                   │ Yes (via __call__)     │
│ Common use cases    │ 90% of cases         │ 10% of cases           │
└─────────────────────┴──────────────────────┴────────────────────────┘

Rule of Thumb:
→ Try __init_subclass__ first - it's simpler and handles most cases
→ Only use metaclass if __init_subclass__ cannot do what you need
→ Metaclasses are more powerful but also more complex to maintain
"""

print(summary)

print("\n" + "=" * 70)
print("Real-World Examples:")
print("=" * 70)

examples = """
Django ORM:           Metaclass (complex field descriptors, query generation)
Flask-RESTful:        __init_subclass__ could work (resource registration)
SQLAlchemy:           Metaclass (complex ORM behavior)
Plugin systems:       __init_subclass__ (simple registration)
Enum:                 Metaclass (controls member creation)
Abstract Base Class:  Metaclass (enforces abstract methods)
Dataclasses:          No metaclass! (uses decorator + __post_init__)
Pydantic:             Metaclass (field validation, serialization)
"""

print(examples)
