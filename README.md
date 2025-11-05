# Python Metaprogramming Examples

This repository contains examples of advanced Python metaprogramming techniques, focusing on the Decorator Pattern implemented using metaclasses and dynamic method manipulation.

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

### 3. Detailed Explanation Files

- **explanation_make_wrapper.py**: Step-by-step walkthrough showing how the metaclass and decorator registration work with debug output
- **diagram_explanation.md**: Visual diagrams and detailed explanation of the timing and mechanics of the pattern

## Understanding the Pattern

The extendable decorator pattern uses several advanced concepts:

1. **Metaclass**: Runs at class definition time to wrap methods
2. **Closures**: `make_wrapper` captures method-specific variables
3. **Late Binding**: Wrappers check for decorators at runtime, not creation time
4. **Dynamic Registration**: Decorators register themselves with the component
5. **Stub Generation**: BaseDecorator creates no-op methods for unimplemented methods

## Use Cases

This pattern is useful when:
- You need to extend object behavior dynamically at runtime
- Multiple independent extensions need to be composed
- You want to avoid the "wrapper hell" of traditional decorators
- You need clean separation between core functionality and extensions

## Running the Examples

All examples are standalone Python scripts:

```bash
# Simple decorator pattern
python decorator_pattern.py

# Advanced extendable pattern
python extendable_decorator_pattern.py

# Detailed explanation with debug output
python explanation_make_wrapper.py
```

## Key Takeaways

- **Metaclasses** can automatically modify class behavior at definition time
- **Late binding** allows decorators to be added/removed dynamically
- **Closure functions** like `make_wrapper` are essential for capturing per-method state
- The pattern provides a clean way to extend functionality without modifying original classes
