# How make_wrapper and _decorators Work Together

## The Key Insight: Late Binding

The wrapper is created **early** but checks for decorators **late**.

---

## Timeline Diagram

```
TIME ──────────────────────────────────────────────────────────────────────►

┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: CLASS DEFINITION (Python interprets "class Coffee:...")       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Metaclass runs:                                                        │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ for each @extendable method:                                      │ │
│  │    original_method = the method                                   │ │
│  │    wrapper = make_wrapper(method_name, original_method)           │ │
│  │    replace method with wrapper                                    │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  Result: Coffee.prepare is now a WRAPPER FUNCTION                      │
│          (but no instances exist yet, no decorators exist yet)         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: INSTANCE CREATION (coffee = Coffee())                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  coffee = Coffee()                                                      │
│  ┌─────────────────────┐                                               │
│  │ Coffee instance     │                                               │
│  │ ─────────────────   │                                               │
│  │ name: "Coffee"      │                                               │
│  │                     │  ← No _decorators yet!                        │
│  └─────────────────────┘                                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: DECORATOR ATTACHMENT (MilkDecorator(coffee))                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  milk = MilkDecorator(coffee)                                           │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │ BaseDecorator.__init__ runs:                                   │    │
│  │                                                                 │    │
│  │   if not hasattr(component, '_decorators'):                    │    │
│  │       component._decorators = []  ← CREATE THE LIST            │    │
│  │                                                                 │    │
│  │   component._decorators.append(self)  ← ADD SELF TO LIST       │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  Now coffee looks like:                                                 │
│  ┌─────────────────────┐                                               │
│  │ Coffee instance     │                                               │
│  │ ─────────────────   │                                               │
│  │ name: "Coffee"      │                                               │
│  │ _decorators: [milk] │  ← LIST CREATED AND POPULATED!                │
│  └─────────────────────┘                                               │
│                                                                         │
│  sugar = SugarDecorator(coffee)  # Adds to existing list               │
│  ┌─────────────────────┐                                               │
│  │ Coffee instance     │                                               │
│  │ ─────────────────   │                                               │
│  │ name: "Coffee"      │                                               │
│  │ _decorators:        │                                               │
│  │   [milk, sugar]     │  ← LIST GROWS!                                │
│  └─────────────────────┘                                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 4: METHOD CALL (coffee.prepare())                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  coffee.prepare()  ← Calls the WRAPPER (created in Phase 1)            │
│                                                                         │
│  Wrapper executes:                                                      │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │ def wrapper(self, *args, **kwargs):                            │    │
│  │                                                                 │    │
│  │     # 1. Call original method                                  │    │
│  │     result = original_method(self, *args, **kwargs)            │    │
│  │                                                                 │    │
│  │     # 2. NOW check for decorators (LATE BINDING!)              │    │
│  │     if hasattr(self, '_decorators') and self._decorators:      │    │
│  │         for decorator in self._decorators:  ← LOOP THE LIST    │    │
│  │             decorator.prepare(*args, **kwargs)                 │    │
│  │                                                                 │    │
│  │     return result                                              │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  Execution order:                                                       │
│  1. Coffee.prepare()     → "Preparing coffee..."                       │
│  2. milk.prepare()       → "Adding milk..."                            │
│  3. sugar.prepare()      → "Adding sugar..."                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Why make_wrapper Doesn't Need to Know Decorators in Advance

### The wrapper is a "smart" function that:

1. **Created early**: When the class is defined (no decorators yet)
2. **Executes late**: When methods are called (decorators may exist now)
3. **Checks dynamically**: Looks for `_decorators` at runtime

### Analogy:

Think of the wrapper like a **mail carrier**:
- The mail carrier is hired when the building is built (class creation)
- They don't need to know who lives in each apartment yet
- When delivering mail, they check the current tenant list (runtime check)
- New tenants can move in anytime (decorators can be added dynamically)

---

## How _decorators List Gets Populated

```python
# Step 1: Create component
coffee = Coffee()  # coffee._decorators doesn't exist yet

# Step 2: Attach first decorator
milk = MilkDecorator(coffee)
    ↓
BaseDecorator.__init__ runs:
    if not hasattr(coffee, '_decorators'):
        coffee._decorators = []  ← LIST CREATED HERE
    coffee._decorators.append(milk)  ← MILK ADDED

# Step 3: Attach second decorator
sugar = SugarDecorator(coffee)
    ↓
BaseDecorator.__init__ runs:
    # List already exists, skip creation
    coffee._decorators.append(sugar)  ← SUGAR ADDED

# Now coffee._decorators = [milk, sugar]
```

---

## The Power of This Pattern

### You can manipulate decorators dynamically:

```python
coffee = Coffee()

# Add decorators
milk = MilkDecorator(coffee)
sugar = SugarDecorator(coffee)

coffee.prepare()  # Uses both decorators

# Remove a decorator
coffee._decorators.remove(milk)

coffee.prepare()  # Now only uses sugar decorator

# Add another decorator later
vanilla = VanillaDecorator(coffee)

coffee.prepare()  # Uses sugar and vanilla
```

### This works because the wrapper checks the list every time it's called!

---

## Common Pitfall: Why We Need make_wrapper

If we wrote the metaclass without `make_wrapper`:

```python
# WRONG - Don't do this!
for key, value in namespace.items():
    if hasattr(value, '_extendable'):
        def wrapper(self, *args, **kwargs):
            result = value(self, *args, **kwargs)  # ← Problem!
            # ... call decorators
            return result
        namespace[key] = wrapper
```

**Problem**: All wrappers would reference the SAME `value` (the last method in the loop)
due to Python's closure over loop variables.

**Solution**: `make_wrapper` creates a NEW closure for each method, capturing its
specific `method_name` and `original` function.

```python
# CORRECT
def make_wrapper(method_name, original):  # ← Captures these per method
    def wrapper(self, *args, **kwargs):
        result = original(self, *args, **kwargs)  # ← Each wrapper has its own
        # ... call decorators using method_name
        return result
    return wrapper

for key, value in namespace.items():
    if hasattr(value, '_extendable'):
        namespace[key] = make_wrapper(key, value)  # ← Creates unique closure
```
