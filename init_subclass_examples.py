"""
__init_subclass__ Examples - Plugin Registry and Validation

__init_subclass__ is a simpler alternative to metaclasses for many use cases.
It was introduced in Python 3.6 and is called whenever a class is subclassed.

When to use __init_subclass__ vs Metaclass:
- Use __init_subclass__ when you only need to customize subclass creation
- Use Metaclass when you need to customize instance creation or method calls
"""


# ============================================================================
# Example 1: Plugin Registry Pattern
# ============================================================================

class PluginRegistry:
    """
    Automatically registers all subclasses in a registry.
    This is one of the most common use cases for __init_subclass__.
    """
    _plugins = {}

    def __init_subclass__(cls, plugin_name=None, **kwargs):
        """
        Called when a class inherits from PluginRegistry.

        Args:
            plugin_name: Optional name for the plugin. If not provided, uses class name.
            **kwargs: Passed to super().__init_subclass__()
        """
        super().__init_subclass__(**kwargs)

        # Use provided name or default to class name
        name = plugin_name or cls.__name__

        print(f"Registering plugin: {name} -> {cls}")

        # Register the plugin
        cls._plugins[name] = cls

        # Store the plugin name on the class
        cls.plugin_name = name

    @classmethod
    def get_plugin(cls, name):
        """Get a plugin by name"""
        return cls._plugins.get(name)

    @classmethod
    def list_plugins(cls):
        """List all registered plugins"""
        return list(cls._plugins.keys())


# Plugins are automatically registered when defined
class ImageProcessor(PluginRegistry, plugin_name="image"):
    def process(self, data):
        return f"Processing image: {data}"


class VideoProcessor(PluginRegistry, plugin_name="video"):
    def process(self, data):
        return f"Processing video: {data}"


class AudioProcessor(PluginRegistry):  # Uses class name as plugin name
    def process(self, data):
        return f"Processing audio: {data}"


# ============================================================================
# Example 2: Validation and Required Attributes
# ============================================================================

class ValidatedClass:
    """
    Enforces that subclasses define required attributes and validates them.
    """
    required_attributes = []

    def __init_subclass__(cls, validate=True, **kwargs):
        super().__init_subclass__(**kwargs)

        # Skip validation if explicitly disabled (for base classes)
        if not validate:
            return

        # Check for required attributes
        missing = []
        for attr in cls.required_attributes:
            if not hasattr(cls, attr):
                missing.append(attr)

        if missing:
            raise TypeError(
                f"{cls.__name__} must define: {', '.join(missing)}"
            )

        # Validate attribute types if type hints are provided
        if hasattr(cls, '__annotations__'):
            for attr, expected_type in cls.__annotations__.items():
                if hasattr(cls, attr):
                    value = getattr(cls, attr)
                    if not isinstance(value, expected_type):
                        raise TypeError(
                            f"{cls.__name__}.{attr} must be {expected_type}, "
                            f"got {type(value)}"
                        )


class DatabaseModel(ValidatedClass, validate=False):
    """Base class for database models with validation"""
    required_attributes = ['table_name', 'fields']

    table_name: str
    fields: list


class UserModel(DatabaseModel):
    """Valid model - has all required attributes with correct types"""
    table_name = "users"
    fields = ["id", "name", "email"]


# This would raise TypeError: ProductModel must define: fields
# class ProductModel(DatabaseModel):
#     table_name = "products"


# ============================================================================
# Example 3: Automatic Method Decoration
# ============================================================================

def timing_decorator(func):
    """Decorator that prints when methods are called"""
    def wrapper(*args, **kwargs):
        print(f"  -> Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"  <- Finished {func.__name__}")
        return result
    wrapper.__name__ = func.__name__
    return wrapper


class AutoDecoratedMethods:
    """
    Automatically decorates methods based on naming convention or markers.
    """
    def __init_subclass__(cls, decorate_pattern=None, **kwargs):
        super().__init_subclass__(**kwargs)

        # If no pattern specified, decorate all methods starting with 'api_'
        pattern = decorate_pattern or 'api_'

        for name, method in cls.__dict__.items():
            if callable(method) and name.startswith(pattern):
                setattr(cls, name, timing_decorator(method))


class APIClient(AutoDecoratedMethods):
    """API client with automatically decorated methods"""

    def api_get_user(self, user_id):
        return f"User {user_id}"

    def api_create_user(self, name):
        return f"Created user: {name}"

    def helper_method(self):
        """This won't be decorated (doesn't start with api_)"""
        return "Helper"


class CustomClient(AutoDecoratedMethods, decorate_pattern='public_'):
    """Custom client with different decoration pattern"""

    def public_action(self):
        return "Public action"

    def private_action(self):
        return "Private action"


# ============================================================================
# Example 4: Serialization Support
# ============================================================================

import json
from typing import get_type_hints


class Serializable:
    """
    Adds serialization capabilities to subclasses based on type hints.
    """
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Store type hints for serialization/deserialization
        if hasattr(cls, '__annotations__'):
            cls._fields = get_type_hints(cls)
        else:
            cls._fields = {}

    def to_dict(self):
        """Convert instance to dictionary"""
        return {
            field: getattr(self, field)
            for field in self._fields
            if hasattr(self, field)
        }

    def to_json(self):
        """Convert instance to JSON"""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data):
        """Create instance from dictionary"""
        instance = cls()
        for field, value in data.items():
            if field in cls._fields:
                setattr(instance, field, value)
        return instance


class Person(Serializable):
    """Person with automatic serialization"""
    name: str
    age: int
    email: str

    def __init__(self, name="", age=0, email=""):
        self.name = name
        self.age = age
        self.email = email


# ============================================================================
# Example 5: Abstract Method Enforcement (simpler than ABC)
# ============================================================================

class RequiresMethods:
    """
    Enforces that subclasses implement specific methods.
    Simpler alternative to ABC for basic cases.
    """
    required_methods = []

    def __init_subclass__(cls, validate=True, **kwargs):
        super().__init_subclass__(**kwargs)

        # Skip validation if explicitly disabled (for base classes)
        if not validate:
            return

        missing = []
        for method_name in cls.required_methods:
            # Check if method is defined in this class (not inherited from RequiresMethods)
            method = getattr(cls, method_name, None)
            if method is None or method is getattr(RequiresMethods, method_name, None):
                missing.append(method_name)

        if missing:
            raise TypeError(
                f"{cls.__name__} must implement: {', '.join(missing)}"
            )


class DataSource(RequiresMethods, validate=False):
    """Base class for data sources"""
    required_methods = ['connect', 'fetch', 'close']


class PostgresSource(DataSource):
    """Valid data source - implements all required methods"""

    def connect(self):
        return "Connected to PostgreSQL"

    def fetch(self, query):
        return f"Fetching: {query}"

    def close(self):
        return "Connection closed"


# This would raise TypeError: RedisSource must implement: fetch, close
# class RedisSource(DataSource):
#     def connect(self):
#         return "Connected to Redis"


# ============================================================================
# Running Examples
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Example 1: Plugin Registry Pattern")
    print("=" * 70)

    print("\nRegistered plugins:", PluginRegistry.list_plugins())

    # Get and use a plugin
    image_plugin = PluginRegistry.get_plugin("image")
    processor = image_plugin()
    print(processor.process("photo.jpg"))

    print("\n" + "=" * 70)
    print("Example 2: Validation and Required Attributes")
    print("=" * 70)

    print(f"\nUserModel table: {UserModel.table_name}")
    print(f"UserModel fields: {UserModel.fields}")

    # Try to create invalid model (uncomment to see error)
    # class InvalidModel(DatabaseModel):
    #     table_name = "invalid"

    print("\n" + "=" * 70)
    print("Example 3: Automatic Method Decoration")
    print("=" * 70)

    client = APIClient()
    print("\nCalling api_get_user:")
    client.api_get_user(123)

    print("\nCalling helper_method (not decorated):")
    client.helper_method()

    print("\nCustom decoration pattern:")
    custom = CustomClient()
    custom.public_action()

    print("\n" + "=" * 70)
    print("Example 4: Serialization Support")
    print("=" * 70)

    person = Person("Alice", 30, "alice@example.com")
    print("\nPerson as dict:", person.to_dict())
    print("\nPerson as JSON:")
    print(person.to_json())

    # Deserialize
    data = {"name": "Bob", "age": 25, "email": "bob@example.com"}
    person2 = Person.from_dict(data)
    print(f"\nDeserialized: {person2.name}, {person2.age}, {person2.email}")

    print("\n" + "=" * 70)
    print("Example 5: Abstract Method Enforcement")
    print("=" * 70)

    db = PostgresSource()
    print(f"\n{db.connect()}")
    print(db.fetch("SELECT * FROM users"))
    print(db.close())

    print("\n" + "=" * 70)
    print("Key Takeaways")
    print("=" * 70)
    print("""
1. __init_subclass__ is called when a class is subclassed
2. It's simpler than metaclasses for common use cases
3. Perfect for: plugin registries, validation, automatic decoration
4. Can accept keyword arguments for configuration
5. Always call super().__init_subclass__(**kwargs) for compatibility

When to use __init_subclass__ vs Metaclass:
- __init_subclass__: Customize subclass creation (most cases)
- Metaclass: Customize instance creation, method calls, or complex behavior
    """)
