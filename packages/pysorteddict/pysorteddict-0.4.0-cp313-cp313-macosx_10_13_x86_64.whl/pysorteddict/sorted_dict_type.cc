#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <cmath>
#include <iterator>
#include <map>
#include <memory>
#include <string>

#include "sorted_dict_type.hh"
#include "sorted_dict_type_key_compare.hh"

#define LEFT_PARENTHESIS "\u0028"
#define RIGHT_PARENTHESIS "\u0029"
#define LEFT_CURLY_BRACKET "\u007B"
#define RIGHT_CURLY_BRACKET "\u007D"

/**
 * C++-style clean-up implementation for Python objects.
 */
struct PyObject_Delete
{
    void operator()(PyObject* ob)
    {
        Py_XDECREF(ob);
    }
};

using PyObjectWrapper = std::unique_ptr<PyObject, PyObject_Delete>;

void SortedDictType::deinit(void)
{
    for (auto& item : *this->map)
    {
        Py_DECREF(item.first);
        Py_DECREF(item.second);
    }
    Py_XDECREF(this->key_type);
    delete this->map;
}

/**
 * Check whether the key type of this sorted dictionary is set and whether the
 * given key-value pair can be inserted into this sorted dictionary. If the
 * value is not supplied, check whether it is valid to get or delete the key.
 * On failure, set a Python exception.
 *
 * @param key Key.
 * @param value Value.
 *
 * @return `true` if the check succeeds, else `false`.
 */
bool SortedDictType::are_key_type_and_key_value_pair_okay(PyObject* key, PyObject* value = nullptr)
{
    bool key_type_set_here = false;
    if (this->key_type == nullptr)
    {
        if (value == nullptr)
        {
            // No key-value pairs have been inserted, so can't get or delete
            // anything.
            PyErr_SetString(PyExc_ValueError, "key type not set: insert at least one item first");
            return false;
        }

        // The first key-value pair is being inserted.
        static PyTypeObject* allowed_key_types[] = {
            &PyBytes_Type,
            &PyFloat_Type,
            &PyLong_Type,
            &PyUnicode_Type,
        };
        for (PyTypeObject* allowed_key_type : allowed_key_types)
        {
            if (Py_IS_TYPE(key, allowed_key_type) != 0)
            {
                // Don't increment the reference count yet. There is one more
                // check remaining.
                this->key_type = allowed_key_type;
                key_type_set_here = true;
                break;
            }
        }
        if (this->key_type == nullptr)
        {
            PyErr_Format(PyExc_TypeError, "unsupported key type: %R", Py_TYPE(key));
            return false;
        }
    }

    // At this point, the key type (member) is guaranteed to be non-null.
    if (!key_type_set_here && Py_IS_TYPE(key, this->key_type) == 0)
    {
        PyErr_Format(PyExc_TypeError, "wrong key type: want %R, got %R", this->key_type, Py_TYPE(key));
        return false;
    }

    // At this point, the key (argument) is guaranteed to be of the correct
    // type.
    if (this->key_type == &PyFloat_Type && std::isnan(PyFloat_AS_DOUBLE(key)))
    {
        PyErr_Format(PyExc_ValueError, "bad key: %R", key);
        if (key_type_set_here)
        {
            // Insertion of the key-value pair was unsuccessful, so clear the
            // key type.
            this->key_type = nullptr;
        }
        return false;
    }

    if (key_type_set_here)
    {
        // Increment the reference count, since this wasn't done above.
        Py_INCREF(this->key_type);
    }
    return true;
}

PyObject* SortedDictType::repr(void)
{
    char const* delimiter = "";
    char const* actual_delimiter = ", ";
    std::string this_repr = "SortedDict" LEFT_PARENTHESIS LEFT_CURLY_BRACKET;
    for (auto& item : *this->map)
    {
        PyObjectWrapper key_repr(PyObject_Repr(item.first));  // 🆕
        if (key_repr == nullptr)
        {
            return nullptr;
        }
        PyObjectWrapper value_repr(PyObject_Repr(item.second));  // 🆕
        if (value_repr == nullptr)
        {
            return nullptr;
        }
        Py_ssize_t key_repr_size, value_repr_size;
        char const* key_repr_utf8 = PyUnicode_AsUTF8AndSize(key_repr.get(), &key_repr_size);
        char const* value_repr_utf8 = PyUnicode_AsUTF8AndSize(value_repr.get(), &value_repr_size);
        this_repr.append(delimiter)
            .append(key_repr_utf8, key_repr_size)
            .append(": ")
            .append(value_repr_utf8, value_repr_size);
        delimiter = actual_delimiter;
    }
    this_repr.append(RIGHT_CURLY_BRACKET RIGHT_PARENTHESIS);
    return PyUnicode_FromStringAndSize(this_repr.data(), this_repr.size());  // 🆕
}

/**
 * Check whether a key is present.
 *
 * @param ob Python object.
 *
 * @return 1 if it is present, else 0.
 */
int SortedDictType::contains(PyObject* key)
{
    if (this->key_type == nullptr || Py_IS_TYPE(key, this->key_type) == 0 || this->map->find(key) == this->map->end())
    {
        return 0;
    }
    return 1;
}

Py_ssize_t SortedDictType::len(void)
{
    return this->map->size();
}

/**
 * Find the value mapped to a key. On failure, set a Python exception.
 *
 * @param key Key.
 *
 * @return Value if present, else `nullptr`.
 */
PyObject* SortedDictType::getitem(PyObject* key)
{
    if (!this->are_key_type_and_key_value_pair_okay(key))
    {
        return nullptr;
    }
    auto it = this->map->find(key);
    if (it == this->map->end())
    {
        PyErr_SetObject(PyExc_KeyError, key);
        return nullptr;
    }
    return Py_NewRef(it->second);
}

/**
 * Map a value to a key or remove a key-value pair. On failure, set a Python
 * exception.
 *
 * @param key Key.
 * @param value Value.
 *
 * @return 0 if a key-value pair was inserted or removed, else -1.
 */
int SortedDictType::setitem(PyObject* key, PyObject* value)
{
    if (!this->are_key_type_and_key_value_pair_okay(key, value))
    {
        return -1;
    }

    // Insertion will be faster if the approximate location is known. Hence,
    // look for the nearest match.
    auto it = this->map->lower_bound(key);
    bool found = it != this->map->end() && !this->map->key_comp()(key, it->first);

    if (value == nullptr)
    {
        // Remove the key-value pair.
        if (!found)
        {
            PyErr_SetObject(PyExc_KeyError, key);
            return -1;
        }
        Py_DECREF(it->first);
        Py_DECREF(it->second);
        this->map->erase(it);
        return 0;
    }

    // Map the value to the key. This merely stores additional references to
    // the key (if applicable) and the value. If I ever plan to allow mutable
    // types as keys, I should store references to their copies instead. Like
    // the C++ standard library containers do.
    if (!found)
    {
        // Insert a new key-value pair. The hint is correct; the key will get
        // inserted just before it.
        it = this->map->emplace_hint(it, key, value);
        Py_INCREF(it->first);
    }
    else
    {
        // Replace the previously-mapped value.
        Py_DECREF(it->second);
        it->second = value;
    }
    Py_INCREF(it->second);
    return 0;
}

PyObject* SortedDictType::clear(void)
{
    for (auto& item : *this->map)
    {
        Py_DECREF(item.first);
        Py_DECREF(item.second);
    }
    this->map->clear();
    Py_RETURN_NONE;
}

PyObject* SortedDictType::copy(void)
{
    PyTypeObject* type = Py_TYPE(this);
    PyObject* sd_copy = type->tp_alloc(type, 0);  // 🆕
    if (sd_copy == nullptr)
    {
        return nullptr;
    }
    SortedDictType* this_copy = reinterpret_cast<SortedDictType*>(sd_copy);
    this_copy->map = new std::map<PyObject*, PyObject*, SortedDictTypeKeyCompare>(*this->map);
    for (auto& item : *this_copy->map)
    {
        Py_INCREF(item.first);
        Py_INCREF(item.second);
    }
    this_copy->key_type = this->key_type;
    Py_XINCREF(this_copy->key_type);
    return sd_copy;
}

PyObject* SortedDictType::items(void)
{
    PyObject* sd_items = PyList_New(this->map->size());  // 🆕
    if (sd_items == nullptr)
    {
        return nullptr;
    }
    Py_ssize_t idx = 0;
    for (auto& item : *this->map)
    {
        PyObject* sd_item = PyTuple_New(2);  // 🆕
        if (sd_item == nullptr)
        {
            Py_DECREF(sd_items);
            return nullptr;
        }
        PyTuple_SET_ITEM(sd_item, 0, Py_NewRef(item.first));
        PyTuple_SET_ITEM(sd_item, 1, Py_NewRef(item.second));
        PyList_SET_ITEM(sd_items, idx++, sd_item);
    }
    return sd_items;
}

PyObject* SortedDictType::keys(void)
{
    PyObject* sd_keys = PyList_New(this->map->size());  // 🆕
    if (sd_keys == nullptr)
    {
        return nullptr;
    }
    Py_ssize_t idx = 0;
    for (auto& item : *this->map)
    {
        PyList_SET_ITEM(sd_keys, idx++, Py_NewRef(item.first));
    }
    return sd_keys;
}

PyObject* SortedDictType::values(void)
{
    PyObject* sd_values = PyList_New(this->map->size());  // 🆕
    if (sd_values == nullptr)
    {
        return nullptr;
    }
    Py_ssize_t idx = 0;
    for (auto& item : *this->map)
    {
        PyList_SET_ITEM(sd_values, idx++, Py_NewRef(item.second));
    }
    return sd_values;
}

PyObject* SortedDictType::get_key_type(void)
{
    if (this->key_type == nullptr)
    {
        Py_RETURN_NONE;
    }
    return Py_NewRef(this->key_type);
}

int SortedDictType::init(PyObject* args, PyObject* kwargs)
{
    // All initialisation is done immediately after allocation in order to
    // avoid leaving essential members uninitialised. This method is kept to
    // allow adding functionality in the future.
    return 0;
}

PyObject* SortedDictType::New(PyTypeObject* type, PyObject* args, PyObject* kwargs)
{
    PyObject* self = type->tp_alloc(type, 0);  // 🆕
    if (self == nullptr)
    {
        return nullptr;
    }

    // Python's default allocator claims to initialise the contents of the
    // allocated memory to null, but actually writes zeros to it. Hence,
    // explicitly initialise them.
    SortedDictType* sd = reinterpret_cast<SortedDictType*>(self);
    sd->map = new std::map<PyObject*, PyObject*, SortedDictTypeKeyCompare>;
    sd->key_type = nullptr;
    return self;
}
