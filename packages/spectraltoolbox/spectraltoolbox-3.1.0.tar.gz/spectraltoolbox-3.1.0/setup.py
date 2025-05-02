#!/usr/bin/env python

import os

from Cython.Build import cythonize
from setuptools import setup, Extension

if __name__ == '__main__':
    import numpy
    incdir_numpy = numpy.get_include().strip()

    ext_modules = [
        Extension(
            name="polymod",  # as it would be imported
            # may include packages/namespaces separated by `.`
            sources=["src/tools.cpp"],  # all sources are compiled into a single binary file
            include_dirs=[incdir_numpy]
        )
    ]
    ext_modules.extend(
        cythonize(
            [
                Extension(
                    name="orthpol",
                    sources=[
                        "src/orthpol.pyx"
                    ],
                    include_dirs=[incdir_numpy]
                )
            ]
        )
    )

    setup(
        ext_modules=ext_modules
    )
