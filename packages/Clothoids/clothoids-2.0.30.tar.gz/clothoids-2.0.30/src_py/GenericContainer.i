%include "std_string.i"

// Injected C++ code
%{
#include <GenericContainer.hh>
#include <complex>
using namespace std;
using namespace GC_namespace;

/*
  _   _ _   _ _ _ _   _           
 | | | | |_(_) (_) |_(_) ___  ___ 
 | | | | __| | | | __| |/ _ \/ __|
 | |_| | |_| | | | |_| |  __/\__ \
  \___/ \__|_|_|_|\__|_|\___||___/
                                  
*/

static int dict_into_gc(PyObject *obj, GenericContainer *gc);

/* From GC to Python Dictionary ***********************************************/

static int array_into_dict(PyObject *obj, GenericContainer *gc, string key) {
  if (PyList_Check(obj)) {
    for (size_t i = 0; i < PyList_Size(obj); i++) {
      PyObject *item = PyList_GET_ITEM(obj, i);
      if (PyInt_Check(item)) {
        (*gc)[i] = (long_type)PyInt_AsLong(item);
      } else if (PyFloat_Check(item)) {
        (*gc)[i] = PyFloat_AsDouble(item);
      } else if (PyComplex_Check(item)) {
        Py_complex pc = PyComplex_AsCComplex(item);
        complex<double> c = complex<double>(pc.real, pc.imag);
        (*gc)[i] = c;
      } else if (PyUnicode_Check(item)) {
        (*gc)[i] = PyUnicode_AsUTF8(item);
      } else if (PyString_Check(item)) {
        (*gc)[i] = PyString_AsString(item);
      } else if (PyBool_Check(item)) {
        (*gc)[i] = (bool)(item == Py_True);
      } else if (PyList_Check(item)) {
        (*gc)[i].set_vector(PyList_Size(item));
        if (array_into_dict(item, &(*gc)[i], key))
          return 1;
      } else if (PyDict_Check(item)) {
        GenericContainer sub = GenericContainer();
        dict_into_gc(item, &sub);
        (*gc)[i] = sub;
      } else {
        PyErr_SetString(PyExc_TypeError, "unsupported type in list");
        return 1;
      }
    }
  } else {
    PyErr_SetString(PyExc_TypeError, (string("not a list ") + key).c_str());
    return 1;
  }
  return 0;
}

static int dict_into_gc(PyObject *obj, GenericContainer *gc) {
  PyObject *key, *value;
  char const *kstr = NULL;
  Py_ssize_t pos = 0;

  while (PyDict_Next(obj, &pos, &key, &value)) {
    kstr = PyUnicode_AsUTF8(key);
    if (PyInt_Check(value)) {
      (*gc)[kstr] = (long_type)PyInt_AsLong(value);
    } else if (PyFloat_Check(value)) {
      (*gc)[kstr] = PyFloat_AsDouble(value);
    } else if (PyComplex_Check(value)) {
      Py_complex pc = PyComplex_AsCComplex(value);
      complex<double> c = complex<double>(pc.real, pc.imag);
      (*gc)[kstr] = c;
    } else if (PyUnicode_Check(value)) {
      (*gc)[kstr] = PyUnicode_AsUTF8(value);
    } else if (PyString_Check(value)) {
      (*gc)[kstr] = PyString_AsString(value);
    } else if (PyBool_Check(value)) {
      (*gc)[kstr] = (bool)(value == Py_True);
    } else if (PyList_Check(value)) {
      (*gc)[kstr].set_vector(PyList_Size(value));
      if (array_into_dict(value, &(*gc)[kstr], kstr))
        return 1;
    } else if (PyDict_Check(value)) {
      GenericContainer sub = GenericContainer();
      dict_into_gc(value, &sub);
      (*gc)[kstr] = sub;
    } else {
      PyErr_SetString(PyExc_TypeError, (string("unsupported type in dictionary at key \"") + kstr + "\"").c_str());
      return 1;
    }
  }
  return 0;
}

/* From Python Dictionary to GC ***********************************************/

static void PyObj_add_item(PyObject *obj, string key, PyObject *value) {
  PyDict_SetItemString(obj, key.c_str(), value);
}

static void PyObj_add_item(PyObject *obj, Py_ssize_t index, PyObject *value) {
  PyList_SetItem(obj, index, value);
}

template <typename T>
static int gc_into_dict(GenericContainer const *gc, PyObject *obj, 
                        T key = nullptr) {
  // The root object must be a dictionary: function has two parameters
  if constexpr (std::is_same<T, nullptr_t>::value) {
    map_type const &m = gc->get_map();
    if (gc->get_type() == TypeAllowed::MAP)
      for (map_type::const_iterator it = m.begin(); it != m.end(); ++it) {
        gc_into_dict<char const *>(&it->second, obj, it->first.c_str());
      }
    else {
      PyErr_SetString(PyExc_TypeError, "Root element of GenericContainer is not a map");
      return 1;
    }
    return 0;
  }
  // Function has beenm called recursively on an element of root dictionary
  switch (gc->get_type()) {
  case TypeAllowed::BOOL:
    if (gc->get_bool())
      PyObj_add_item(obj, key, Py_True);
    else
      PyObj_add_item(obj, key, Py_False);
    break;
  case TypeAllowed::INTEGER:
    PyObj_add_item(obj, key, PyInt_FromLong((long_type)gc->get_int()));
    break;
  case TypeAllowed::LONG:
    PyObj_add_item(obj, key, PyInt_FromLong((long_type)gc->get_long()));
    break;
  case TypeAllowed::REAL:
    PyObj_add_item(obj, key, PyFloat_FromDouble(gc->get_real()));
    break;
  case TypeAllowed::COMPLEX: {
    real_type re, im;
    gc->get_complex_number(re, im);
    PyObject *c = PyComplex_FromDoubles(re, im);
    PyObj_add_item(obj, key, c);
  } break;
  case TypeAllowed::STRING:
    PyObj_add_item(obj, key, PyString_FromString(gc->get_string().c_str()));
    break;
  case TypeAllowed::VECTOR: {
    vector_type const &v = gc->get_vector();
    PyObject *data = PyList_New(v.size());
    for (Py_ssize_t i = 0; i < v.size(); ++i) {
      gc_into_dict<Py_ssize_t>(&v[i], data, i);
    }
    PyObj_add_item(obj, key, data);
  } break;
  case TypeAllowed::MAP: {
    map_type const &m = gc->get_map();
    PyObject *data = PyDict_New();
    for (map_type::const_iterator it = m.begin(); it != m.end(); ++it) {
      gc_into_dict<char const *>(&it->second, data, it->first.c_str());
    }
    PyObj_add_item(obj, key, data);
  } break;
  default:
    PyErr_SetString(
        PyExc_TypeError,
        (string("Type not managed: ") + gc->get_type_name()).c_str());
    return 1;
  }
  return 0;
}
%}


/*
  _____                                             ___ _   _ 
 |_   _|   _ _ __   ___ _ __ ___   __ _ _ __  ___  |_ _| \ | |
   | || | | | '_ \ / _ \ '_ ` _ \ / _` | '_ \/ __|  | ||  \| |
   | || |_| | |_) |  __/ | | | | | (_| | |_) \__ \  | || |\  |
   |_| \__, | .__/ \___|_| |_| |_|\__,_| .__/|___/ |___|_| \_|
       |___/|_|                        |_|                    
*/
%typemap(in) GC_namespace::GenericContainer &gc {
  if (PyDict_Check($input)) {
    $1 = new GenericContainer();
    if (dict_into_gc($input, $1))
      SWIG_fail;
  }
  // complain and fail 
  else {
    PyErr_SetString(PyExc_TypeError, "not a dictionary");
    SWIG_fail;
  }
}
%typemap(freearg) GC_namespace::GenericContainer &gc {
  if ($1) delete $1;
}


/*
  _____                                              ___  _   _ _____ 
 |_   _|   _ _ __   ___ _ __ ___   __ _ _ __  ___   / _ \| | | |_   _|
   | || | | | '_ \ / _ \ '_ ` _ \ / _` | '_ \/ __| | | | | | | | | |  
   | || |_| | |_) |  __/ | | | | | (_| | |_) \__ \ | |_| | |_| | | |  
   |_| \__, | .__/ \___|_| |_| |_|\__,_| .__/|___/  \___/ \___/  |_|  
       |___/|_|                        |_|                            
*/

%typemap(out) string {
  $result = PyString_FromString($1.c_str());
}

%typemap(out) GC_namespace::GenericContainer {
  // Dictionary typemap
  $result = PyDict_New();
  if (gc_into_dict<nullptr_t>(&$1, $result)) 
    SWIG_fail;
}
