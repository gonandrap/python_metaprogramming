# Python Metaprogramming Examples

This repository contains comprehensive examples of advanced Python metaprogramming techniques, including:
- Decorator Pattern using metaclasses and dynamic method manipulation
- `__init_subclass__` hook for simpler class customization
- Practical comparisons showing when to use each approach

## Examples

### 1. Simple Decorator Pattern (`decorator_pattern.py`)

A basic introduction to decorator patterns using metaprogramming:

- **DecoratorMeta**: A metaclass that automatically applies decorators to methods based on naming conventions (methods starting with `do_`)
- **Function Decorator**: `log_calls` decorator that logs when functions are called
- **Class Decorator**: `add_timestamp` decorator that adds timestamp functionality to classes

**Key Features:**
- Automatic method decoration via metaclass
- Naming convention-based decorator application
- Class-level decoration for adding functionality

**Run Example:**
```bash
python decorator_pattern.py
```

### 2. Extendable Decorator Pattern (`extendable_decorator_pattern.py`)

An advanced implementation where decorators extend a base class and selectively override methods:

- **@extendable**: Decorator to mark methods as extendable
- **ExtendableMeta**: Metaclass that wraps extendable methods to automatically call decorator methods after execution
- **BaseDecorator**: Base class that dynamically creates stub methods for all extendable methods
- Child decorators only override the methods they want to extend

**Key Features:**
- Late binding: Decorators can be attached/removed at runtime
- Selective method overriding: Decorators only implement methods they care about
- Multiple decorators: Stack multiple decorators on a single object
- Automatic method chaining: Original method + all decorator methods execute in sequence

**Architecture:**
1. Class with `@extendable` methods uses `ExtendableMeta` metaclass
2. Metaclass wraps each extendable method to call decorator methods after execution
3. `BaseDecorator` provides empty implementations for all extendable methods
4. Child decorators override only the methods they want to extend
5. When an extendable method is called, all decorator methods are automatically invoked

**Run Example:**
```bash
python extendable_decorator_pattern.py
```

### 3. `__init_subclass__` Examples (`init_subclass_examples.py`)

A comprehensive guide to `__init_subclass__`, a simpler alternative to metaclasses for many use cases (Python 3.6+):

**Five Practical Examples:**

1. **Plugin Registry Pattern**: Automatically register subclasses for plugin systems
2. **Validation & Required Attributes**: Enforce that subclasses define specific attributes
3. **Automatic Method Decoration**: Decorate methods based on naming patterns
4. **Serialization Support**: Add JSON serialization based on type hints
5. **Abstract Method Enforcement**: Require subclasses to implement specific methods

**Key Features:**
- Simpler than metaclasses for most use cases
- Accepts keyword arguments for configuration
- Perfect for plugin systems, validation, and automatic decoration
- More readable and maintainable than metaclasses

**Run Example:**
```bash
python init_subclass_examples.py
```

### 4. `__init_subclass__` vs Metaclass Comparison (`init_subclass_vs_metaclass.py`)

Side-by-side comparison showing when to use each approach:

**Comparison Examples:**
- Plugin Registry: Both work, `__init_subclass__` is simpler
- Method Call Interception: Only metaclass can do this (Singleton pattern)
- Attribute Access Control: Only metaclass can intercept attribute access
- Automatic Method Decoration: Both work, `__init_subclass__` is clearer
- Parameterized Configuration: `__init_subclass__` makes this very clean

**Decision Guide:**
- Use `__init_subclass__` for 90% of cases (simpler, more maintainable)
- Use metaclass only when you need to control instance creation or attribute access

**Run Example:**
```bash
python init_subclass_vs_metaclass.py
```

### 5. Detailed Explanation Files

- **explanation_make_wrapper.py**: Step-by-step walkthrough showing how the metaclass and decorator registration work with debug output
- **diagram_explanation.md**: Visual diagrams and detailed explanation of the timing and mechanics of the pattern

## Understanding the Patterns

### Metaprogramming Concepts Used

**Decorator Pattern:**
1. **Metaclass**: Runs at class definition time to wrap methods
2. **Closures**: `make_wrapper` captures method-specific variables
3. **Late Binding**: Wrappers check for decorators at runtime, not creation time
4. **Dynamic Registration**: Decorators register themselves with the component
5. **Stub Generation**: BaseDecorator creates no-op methods for unimplemented methods

**`__init_subclass__` Pattern:**
1. **Subclass Hook**: Called automatically when a class is subclassed
2. **Keyword Arguments**: Accept configuration parameters in class definition
3. **Registry Pattern**: Automatically register classes when they're defined
4. **Validation**: Enforce constraints at class creation time
5. **Simplicity**: Cleaner and more maintainable than metaclasses for most cases

### When to Use What

| Technique | Best For | Complexity |
|-----------|----------|------------|
| `__init_subclass__` | Plugin registration, validation, simple decoration | Low |
| Metaclass | Instance creation control, attribute interception | High |
| Decorator (function) | Single function/method enhancement | Very Low |
| Class Decorator | Adding functionality to a class | Low |

## Use Cases

This pattern is useful when:
- You need to extend object behavior dynamically at runtime
- Multiple independent extensions need to be composed
- You want to avoid the "wrapper hell" of traditional decorators
- You need clean separation between core functionality and extensions

## Running the Examples

All examples are standalone Python scripts:

```bash
# Decorator Pattern Examples
python decorator_pattern.py                    # Simple decorator pattern
python extendable_decorator_pattern.py         # Advanced extendable pattern
python explanation_make_wrapper.py             # Detailed explanation with debug

# __init_subclass__ Examples
python init_subclass_examples.py               # Five practical use cases
python init_subclass_vs_metaclass.py           # Comparison and decision guide
```

## Key Takeaways

### Decorator Pattern with Metaclasses
- **Metaclasses** can automatically modify class behavior at definition time
- **Late binding** allows decorators to be added/removed dynamically
- **Closure functions** like `make_wrapper` are essential for capturing per-method state
- The pattern provides a clean way to extend functionality without modifying original classes

### `__init_subclass__` Hook
- **Simpler than metaclasses** for 90% of use cases - start here first!
- **Automatic registration** of subclasses makes plugin systems trivial
- **Keyword arguments** allow elegant configuration in class definition
- **Validation at class creation** catches errors early
- **Only use metaclasses** when you need instance creation control or attribute interception

### General Principles
- Choose the simplest tool that solves your problem
- `__init_subclass__` is usually simpler and more maintainable than metaclasses
- Metaprogramming adds power but also complexity - use judiciously
- Document your metaprogramming patterns well for future maintainers
