import builtins
import platform
import random
import re
import string

import pytest

from pysorteddict import SortedDict

# Reference counting is specific to CPython.
if cpython := platform.python_implementation() == "CPython":
    from sys import getrefcount

supported_types = {bytes, float, int, str}
available_types = {bool, bytearray, bytes, complex, dict, float, frozenset, int, list, set, str, tuple}


class Resources:
    """
    Store resources used to generate similar test cases for different key
    types.
    """

    def __init__(self, key_type: type):
        self.key_type = key_type
        self.available_types = available_types.union({type("sub" + self.key_type.__name__, (self.key_type,), {})})
        self.unsupported_types = self.available_types.difference(supported_types)
        self.wrong_types = self.available_types.difference({self.key_type})

        self.rg = random.Random(__name__)
        self.keys = [self.gen() for _ in range(1000)]
        self.values = [self.gen() for _ in self.keys]
        self.normal_dict = dict(zip(self.keys, self.values, strict=True))

        sorted_dict = SortedDict(self.key_type)
        for key, value in zip(self.keys, self.values, strict=True):
            sorted_dict[key] = value
        self.sorted_dicts = [sorted_dict, sorted_dict.copy()]

        # Store the reference count of an item in a list at the position at
        # which it appears in the normal dictionary. The reference counts are
        # all 4, but querying the reference count increases it, so I store 5.
        # Whenever a test changes the reference count of any item, I set the
        # new reference count at its index.
        self.keys = [*self.normal_dict]
        self.keys_refcounts = [5] * len(self.keys)
        self.values = [*self.normal_dict.values()]
        self.values_refcounts = [5] * len(self.values)

    def gen(self, *, small: bool = True) -> bytes | str | int:
        """
        Generate a key or value for a dictionary. It will be a new object (i.e.
        not an interned one).

        :param small: Whether to generate a small or large key/value. (A small
        one will never be equal to a large one.)

        :return: Random result.
        """
        match self.key_type:
            # The pattern must be non-capturing (otherwise, it raises a syntax
            # error because the remaining patterns become unreachable). Hence,
            # whenever the pattern is an existing name which can be shadowed,
            # it has to be written like this.
            case builtins.bytes:
                lo, hi = (8, 16) if small else (16, 32)
                return self.rg.randbytes(self.rg.randrange(lo, hi))
            case builtins.float:
                if small:
                    return self.rg.uniform(0, 1) if self.rg.randrange(10) > 0 else -float("inf")
                return self.rg.uniform(10, 100) if self.rg.randrange(10) > 0 else float("inf")
            case builtins.int:
                lo, hi = (1000, 2000) if small else (2000, 3000)
                return self.rg.randrange(lo, hi)
            case builtins.str:
                lo, hi = (10, 20) if small else (20, 30)
                return "".join(self.rg.choices(string.ascii_lowercase, k=self.rg.randrange(lo, hi)))
            case _:
                raise RuntimeError


@pytest.fixture
def resources(request):
    """
    Create test resources for the given key type (passed as a parameter to this
    fixture).
    """
    resources = Resources(request.param)
    yield resources

    # Tearing down: verify the reference counts.
    if cpython:
        for observed, expected in zip(map(getrefcount, resources.keys), resources.keys_refcounts, strict=True):
            assert observed == expected
        for observed, expected in zip(map(getrefcount, resources.values), resources.values_refcounts, strict=True):
            assert observed == expected


@pytest.fixture
def sorted_dict(request, resources):
    """
    Obtain either the sorted dictionary or its copy based on the index (passed
    as a parameter to this fixture). The aim is to test both it and its copy
    with the same rigour.
    """
    sorted_dict = resources.sorted_dicts[request.param]
    yield sorted_dict

    # Tearing down: verify some non-mutating methods.
    assert repr(sorted_dict) == f"SortedDict({dict(sorted(resources.normal_dict.items()))})"
    assert len(sorted_dict) == len(resources.normal_dict)
    assert sorted_dict.items() == sorted(resources.normal_dict.items())
    assert sorted_dict.keys() == sorted(resources.normal_dict)
    assert sorted_dict.values() == [item[1] for item in sorted(resources.normal_dict.items())]
    assert sorted_dict.key_type is resources.key_type


# Run each test with each key type, and on the sorted dictionary and its copy.
pytestmark = [
    pytest.mark.parametrize("resources", supported_types, indirect=True),
    pytest.mark.parametrize("sorted_dict", [0, 1], ids=["original", "copy"], indirect=True),
]


def test_contains_wrong_type(resources, sorted_dict):
    for wrong_type in resources.wrong_types:
        assert wrong_type() not in sorted_dict


def test_contains_no(resources, sorted_dict):
    key = resources.gen(small=False)
    assert key not in sorted_dict

    if cpython:
        assert getrefcount(key) == 2


def test_contains_yes(resources, sorted_dict):
    key = resources.rg.choice(resources.keys)
    assert key in sorted_dict

    if cpython:
        assert getrefcount(key) == 6


def test_getitem_wrong_type(resources, sorted_dict):
    for wrong_type in resources.wrong_types:
        with pytest.raises(TypeError, match=f"wrong key type: want {resources.key_type!r}, got {wrong_type!r}"):
            sorted_dict[wrong_type()]


def test_getitem_missing(resources, sorted_dict):
    key = resources.gen(small=False)
    with pytest.raises(KeyError, match=re.escape(str(key))):
        sorted_dict[key]

    if cpython:
        assert getrefcount(key) == 2


def test_getitem_found(resources, sorted_dict):
    key = resources.rg.choice(resources.keys)
    value = sorted_dict[key]
    assert value == resources.normal_dict[key]

    if cpython:
        assert getrefcount(key) == 6
        assert getrefcount(value) == 6


def test_delitem_wrong_type(resources, sorted_dict):
    for wrong_type in resources.wrong_types:
        with pytest.raises(TypeError, match=f"wrong key type: want {resources.key_type!r}, got {wrong_type!r}"):
            del sorted_dict[wrong_type()]


def test_delitem_missing(resources, sorted_dict):
    key = resources.gen(small=False)
    with pytest.raises(KeyError, match=re.escape(str(key))):
        del sorted_dict[key]

    if cpython:
        assert getrefcount(key) == 2


def test_delitem_found(resources, sorted_dict):
    idx, key = resources.rg.choice([*enumerate(resources.keys)])
    del resources.normal_dict[key]
    del sorted_dict[key]
    assert key not in sorted_dict

    if cpython:
        resources.keys_refcounts[idx] -= 2
        resources.values_refcounts[idx] -= 2


def test_setitem_wrong_type(resources, sorted_dict):
    value = resources.gen()
    for wrong_type in resources.wrong_types:
        with pytest.raises(TypeError, match=f"wrong key type: want {resources.key_type!r}, got {wrong_type!r}"):
            sorted_dict[wrong_type()] = value

    if cpython:
        assert getrefcount(value) == 2


def test_setitem_insert(resources, sorted_dict):
    key, value = resources.gen(small=False), resources.gen()
    resources.normal_dict[key] = value
    sorted_dict[key] = value
    assert key in sorted_dict
    assert sorted_dict[key] == value

    if cpython:
        assert getrefcount(key) == 4
        assert getrefcount(value) == 4


def test_setitem_overwrite(resources, sorted_dict):
    idx, key = resources.rg.choice([*enumerate(resources.keys)])
    value = resources.gen()
    resources.normal_dict[key] = value
    sorted_dict[key] = value
    assert key in sorted_dict
    assert sorted_dict[key] == value

    if cpython:
        assert getrefcount(value) == 4
        resources.values_refcounts[idx] -= 2


def test_clear(resources, sorted_dict):
    resources.normal_dict.clear()
    sorted_dict.clear()

    if cpython:
        resources.keys_refcounts = [3] * len(resources.keys)
        resources.values_refcounts = [3] * len(resources.values)


# Although I don't need the second fixture, I am forced to specify it because I
# have marked all tests as using those two fixtures.
def test_empty_sorted_dictionary(resources, sorted_dict):
    sorted_dict = SortedDict()
    assert sorted_dict.key_type is None
    for available_type in resources.available_types:
        assert available_type() not in sorted_dict
        with pytest.raises(ValueError, match="key type not set: insert at least one item first"):
            sorted_dict[available_type()]
        assert sorted_dict.key_type is None
    for unsupported_type in resources.unsupported_types:
        with pytest.raises(TypeError, match=f"unsupported key type: {unsupported_type!r}"):
            sorted_dict[unsupported_type()] = None
        assert sorted_dict.key_type is None


if __name__ == "__main__":
    pytest.main()
