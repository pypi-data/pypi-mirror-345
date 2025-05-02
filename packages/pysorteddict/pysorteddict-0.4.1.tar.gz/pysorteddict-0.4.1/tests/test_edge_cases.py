import pytest

from pysorteddict import SortedDict


@pytest.mark.parametrize("bad_key", [float("nan")])
def test_bad_keys(bad_key):
    sorted_dict = SortedDict()
    with pytest.raises(ValueError, match="key type not set: insert at least one item first"):
        sorted_dict[bad_key]
    with pytest.raises(ValueError, match=f"bad key: {bad_key}"):
        sorted_dict[bad_key] = None
    assert sorted_dict.key_type is None
    sorted_dict[type(bad_key)()] = None
    with pytest.raises(ValueError, match=f"bad key: {bad_key}"):
        sorted_dict[bad_key] = None


if __name__ == "__main__":
    pytest.main()
