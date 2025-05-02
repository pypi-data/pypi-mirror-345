# Pixar TBB

[![CMake](https://img.shields.io/badge/CMake-3.21...3.31-blue.svg?logo=CMake&logoColor=blue)](https://cmake.org)
[![License](https://img.shields.io/badge/License-Apache_2.0-yellow.svg)](https://github.com/uxlfoundation/oneTBB/blob/master/LICENSE.txt)

pxr-tbb bundles [Intel TBB (oneTBB)](https://uxlfoundation.github.io/oneTBB/)
headers and shared libraries into a portable Python wheel, so it can be easily
used to build and install Pixar libraries distributed through PyPI.

# Why not use tbb or tbb-devel?

The existing [tbb](https://pypi.org/project/tbb/) and 
[tbb-devel](https://pypi.org/project/tbb-devel/) packages do not provide enough
prebuilt wheels to support all platforms and Python versions needed for
reliable builds.

