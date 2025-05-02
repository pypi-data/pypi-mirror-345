#ifndef SORTED_DICT_TYPE_HH_
#define SORTED_DICT_TYPE_HH_

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <map>

#include "sorted_dict_type_key_compare.hh"

struct SortedDictType
{
public:
    PyObject_HEAD;

private:
    // Pointer to an object on the heap. Can't be the object itself, because
    // this container will be allocated a definite amount of space, which won't
    // allow the object to grow.
    std::map<PyObject*, PyObject*, SortedDictTypeKeyCompare>* map;

    // The type of each key.
    PyTypeObject* key_type;

private:
    bool are_key_type_and_key_value_pair_okay(PyObject*, PyObject*);

public:
    void deinit(void);
    PyObject* repr(void);
    int contains(PyObject*);
    Py_ssize_t len(void);
    PyObject* getitem(PyObject*);
    int setitem(PyObject*, PyObject*);
    PyObject* clear(void);
    PyObject* copy(void);
    PyObject* items(void);
    PyObject* keys(void);
    PyObject* values(void);
    PyObject* get_key_type(void);
    int init(PyObject*, PyObject*);
    static PyObject* New(PyTypeObject*, PyObject*, PyObject*);
};

#endif
