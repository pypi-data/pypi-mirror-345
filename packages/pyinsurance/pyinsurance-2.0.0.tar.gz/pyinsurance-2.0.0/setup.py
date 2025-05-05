import numpy as np
from Cython.Build import cythonize  # type: ignore
from setuptools import setup  # type: ignore

setup(
    ext_modules=cythonize(
        "pyinsurance/portfolio/_tipp.pyx",
        compiler_directives={
            "language_level": "3",
            "boundscheck": False,
            "wraparound": False,
            "cdivision": True,
            "nonecheck": False,
            "initializedcheck": False,
        },
    ),
    include_dirs=[np.get_include()],
)
