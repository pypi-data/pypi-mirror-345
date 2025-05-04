## Bunch

A simple Python class that allows dictionary-style and attribute-style access to data interchangeably. Think of it as a lightweight object wrapper for dictionaries — great for config objects, JSON responses, or anything else you'd normally throw in a dict.

### <ins> Features </ins>

- Access keys as attributes or like a dictionary
- Convert from regular dictionaries
- Pretty-printed JSON representation
- Check if a value exists
- Fully compatible with `in`, `.keys()`, `.items()`, etc.

### <ins> Installation </ins>

You can install this package via PIP: _pip install bunch_

### <ins> Usage </ins>

```python
# - Mutable Bunch -
from bunch.bunch import Bunch

my_bunch = Bunch({'name': 'Jane', 'age': 30})

print(my_bunch.name)  # Output: Jane
print(my_bunch['age'])  # Output: 30

# - Immutable Bunch -
from bunch.immutable_bunch import ImmutableBunch

my_immutable_bunch = ImmutableBunch({'name': 'John', 'age': 25})
print(my_immutable_bunch.name)  # Output: John
print(my_immutable_bunch['age'])  # Output: 35

# Attempting to modify an ImmutableBunch will raise an Exception
my_immutable_bunch.name = 'Alice'  # Raises ImmutableBunchException
```
