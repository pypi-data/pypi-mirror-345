# pysorteddict

Provides `SortedDict`, which is a Python sorted dictionary: a Python dictionary in which the keys are always in
ascending order.

[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)

[![style](https://github.com/tfpf/pysorteddict/actions/workflows/style.yml/badge.svg)](https://github.com/tfpf/pysorteddict/actions/workflows/style.yml)
[![package](https://github.com/tfpf/pysorteddict/actions/workflows/package.yml/badge.svg)](https://github.com/tfpf/pysorteddict/actions/workflows/package.yml)

<p align="center">
 <img src="https://github.com/user-attachments/assets/e9d1e78e-c0fd-4d87-93f6-e293ddef31ba" />
</p>

## Installation

[pysorteddict is available on PyPI.](https://pypi.org/project/pysorteddict/) It requires Python 3.10 or newer. Built
distributions (binary wheels) are provided for Linux, macOS and Windows, so installing is straightforward.

```shell
pip install pysorteddict
```

If you are on any other platform, install the Python development headers and libraries before running the above
command.

## Usage

All keys in a sorted dictionary must be of the same type, which is determined when the first key-value pair is inserted
into it. The values, though, can be of any type.

```python
import json

from pysorteddict import SortedDict

sorted_dict = SortedDict()
sorted_dict["honestly"] = "weight"
sorted_dict["gain is"] = 31.692
sorted_dict["times"] = "easier than"
sorted_dict["losing"] = ["weight"]
assert sorted_dict.key_type is str
print(json.dumps(sorted_dict, indent=2, sort_keys=False))
```

The above Python script will output the keys in ascending order.

```json
{
  "gain is": 31.692,
  "honestly": "weight",
  "losing": [
    "weight"
  ],
  "times": "easier than"
}
```

The following key types are supported.

* `bytes`
* `float`
* `int`
* `str`

## Implementation Details

pysorteddict is implemented entirely in C++. `SortedDict` provides a Python interface to
`std::map<PyObject*, PyObject*, _>`.

## Documentation

### Constructor

#### `SortedDict(*args, **kwargs) -> SortedDict`

Create an empty sorted dictionary. `args` and `kwargs` are ignored.

### Properties

#### `d.key_type: type | None`

Return the key type of the sorted dictionary `d`, or `None` if no key-value pairs have been inserted in it.

### Magic Methods

#### `repr(d)`

Return a human-readable representation of the sorted dictionary `d`.

#### `key in d`

Return whether `key` is present in the sorted dictionary `d`.

#### `len(d)`

Return the number of key-value pairs in the sorted dictionary `d`.

#### `d[key]`

Return the value mapped to `key` in the sorted dictionary `d`.

If no key-value pairs have been inserted into `d` yet, raise `ValueError`.

```python
from pysorteddict import *
d = SortedDict()
d["foo"]
```

```
Traceback (most recent call last):
  File "…", line 3, in <module>
    d["foo"]
    ~^^^^^^^
ValueError: key type not set: insert at least one item first
```

Otherwise, if `type(key)` does not match the type of the first key inserted into `d`, raise `TypeError`.

```python
from pysorteddict import *
d = SortedDict()
d["foo"] = ("bar", "baz")
d[0xC0FFEE]
```

```
Traceback (most recent call last):
  File "…", line 4, in <module>
    d[0xC0FFEE]
    ~^^^^^^^^^^
TypeError: wrong key type: want <class 'str'>, got <class 'int'>
```

Otherwise, if `key` is not comparable with instances of its type, raise `ValueError`.

```python
from pysorteddict import *
d = SortedDict()
d[1.1] = ("racecar",)
d[float("nan")]
```

```
Traceback (most recent call last):
  File "…", line 4, in <module>
    d[float("nan")]
    ~^^^^^^^^^^^^^^
ValueError: bad key: nan
```

Otherwise, if `key` is not present in `d`, raise `KeyError`.

```python
from pysorteddict import *
d = SortedDict()
d["foo"] = ("bar", "baz")
d["spam"]
```

```
Traceback (most recent call last):
  File "…", line 4, in <module>
    d["spam"]
    ~^^^^^^^^
KeyError: 'spam'
```

#### `d[key] = value`

Map `value` to `key` in the sorted dictionary `d`, replacing the previously-mapped value (if any).

If no key-value pairs have been inserted into `d` yet and `type(key)` isn't one of the supported types (`bytes`,
`float`, `int` and `str`), raise `TypeError`.

```python
from pysorteddict import *
d = SortedDict()
d[["eggs"]] = None
```

```
Traceback (most recent call last):
  File "…", line 3, in <module>
    d[["eggs"]] = None
    ~^^^^^^^^^^
TypeError: unsupported key type: <class 'list'>
```

Otherwise, if `type(key)` does not match the type of the first key inserted into `d`, raise `TypeError`.

```python
from pysorteddict import *
d = SortedDict()
d["foo"] = ("bar", "baz")
d[0xC0FFEE] = "spam"
```

```
Traceback (most recent call last):
  File "…", line 4, in <module>
    d[0xC0FFEE] = "spam"
    ~^^^^^^^^^^
TypeError: wrong key type: want <class 'str'>, got <class 'int'>
```

Otherwise, if `key` is not comparable with instances of its type, raise `ValueError`.

```python
from pysorteddict import *
d = SortedDict()
d[1.1] = ("racecar",)
d[float("nan")] = {}
```

```
Traceback (most recent call last):
  File "…", line 4, in <module>
    d[float("nan")] = {}
    ~^^^^^^^^^^^^^^
ValueError: bad key: nan
```

#### `del d[key]`

Remove `key` and the value mapped to it from the sorted dictionary `d`.

If no key-value pairs have been inserted into `d` yet, raise `ValueError`.

```python
from pysorteddict import *
d = SortedDict()
del d["foo"]
```

```
Traceback (most recent call last):
  File "…", line 3, in <module>
    del d["foo"]
        ~^^^^^^^
ValueError: key type not set: insert at least one item first
```

Otherwise, if `type(key)` does not match the type of the first key inserted into `d`, raise `TypeError`.

```python
from pysorteddict import *
d = SortedDict()
d["foo"] = ("bar", "baz")
del d[0xC0FFEE]
```

```
Traceback (most recent call last):
  File "…", line 4, in <module>
    del d[0xC0FFEE]
        ~^^^^^^^^^^
TypeError: wrong key type: want <class 'str'>, got <class 'int'>
```

Otherwise, if `key` is not comparable with instances of its type, raise `ValueError`.

```python
from pysorteddict import *
d = SortedDict()
d[1.1] = ("racecar",)
del d[float("nan")]
```

```
Traceback (most recent call last):
  File "…", line 4, in <module>
    del d[float("nan")]
        ~^^^^^^^^^^^^^^
ValueError: bad key: nan
```

Otherwise, if `key` is not present in `d`, raise `KeyError`.

```python
from pysorteddict import *
d = SortedDict()
d["foo"] = ("bar", "baz")
del d["spam"]
```

```
Traceback (most recent call last):
  File "…", line 4, in <module>
    del d["spam"]
        ~^^^^^^^^
KeyError: 'spam'
```

### Other Methods

#### `d.clear()`

Remove all key-value pairs in the sorted dictionary `d`.

#### `d.copy() -> SortedDict`

Return a shallow copy of the sorted dictionary `d`.

#### `d.items() -> list[tuple[object, object]]`

Return the key-value pairs in the sorted dictionary `d`. The list will be sorted. It will exist independently of `d`;
it won't be a view on its items.

#### `d.keys() -> list[object]`

Return the keys in the sorted dictionary `d`. The list will be sorted. It will exist independently of ``d``; it won't
be a view on its keys.

#### `d.values() -> list[object]`

Return the values in the sorted dictionary `d`. The list will be sorted by the keys the values are mapped to. It will
exist independently of `d`; it won't be a view on its values.
