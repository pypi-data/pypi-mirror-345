"""
Python setup file for the Clothoids C++ library. It uses the SWIG interface to
generate the Python bindings for the C++ library.

Authors:
 - Sebastiano Taddei
 - Gabriele Masina
"""

import os
from setuptools import setup, Extension

dirname = os.path.dirname(os.path.abspath(__file__))

# Define the include directories
include_dirs = [
    dirname,
    os.path.join(dirname, "lib", "include"),
    os.path.join(dirname, "lib3rd", "include"),
]

# Define the library directories
library_dirs = [
    os.path.join(dirname, "lib", "lib"),
    os.path.join(dirname, "lib3rd", "lib"),
]

# Define the libraries
library_names = []
prefix = "lib"
for library_dir in library_dirs:
    # Get the filenames in the library directory
    filenames = os.listdir(library_dir)

    # For each filename, remove the prefix and suffix
    for filename in filenames:
        # Remove the file extension
        root = os.path.splitext(filename)[0]

        if root.startswith(prefix):
            root = root[len(prefix) :]

        library_names.append(root)

clothoids_module = Extension(
    "_Clothoids",
    sources=[os.path.join("src_py", "Clothoids.i")],
    include_dirs=include_dirs,
    library_dirs=library_dirs,
    libraries=library_names,
    swig_opts=["-c++"],
    extra_compile_args=["-std=c++11"],
)

setup(
    ext_modules=[clothoids_module],
    py_modules=["Clothoids"],
    package_dir={"": "src_py"},
)
