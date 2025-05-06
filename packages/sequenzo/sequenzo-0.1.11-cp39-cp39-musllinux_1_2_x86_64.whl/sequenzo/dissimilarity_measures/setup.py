"""
@Author  : 李欣怡
@File    : setup.py
@Time    : 2025/3/30 16:55
@Desc    : build for Cython
"""
from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np

cython_files = [
    "utils/get_sm_trate_substitution_cost_matrix.pyx",
    "utils/seqconc.pyx",
    "utils/seqdss.pyx",
    "utils/seqdur.pyx",
    "utils/seqlength.pyx"
]

extensions = [
    Extension(
        name="utils." + filename.split("/")[-1].split(".")[0],
        sources=[filename],
        include_dirs=[np.get_include()],
        define_macros=[('NPY_NO_DEPRECATED_API', '1')]
    )
    for filename in cython_files
]

setup(
    name="Sequenzo Cython Extensions",
    ext_modules=cythonize(extensions),
    include_dirs=[np.get_include()],
)


