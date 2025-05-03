
import glob
from setuptools import setup, Extension
import pybind11

__CUPLOADER_NAME__ = "PyCUploader"
__CUPLOADER_VERSION__ = "0.0.1"
__CUPLOADER_AUTHOR__ = "Chunel"
__CUPLOADER_AUTHOR_EMAIL__ = "chunel@foxmail.com"
__CUPLOADER_DESCRIPTION__ = "Chunel test pypi uploader"
__CUPLOADER_URL__ = "https://github.com/ChunelFeng/CPypiUploadDemo"
__CUPLOADER_LICENSE__ = "Apache 2.0"

_sources = ['PyUploadDemo.cpp'] + glob.glob("../src/**/*.cpp", recursive=True)
_extra_compile_args = ["-pthread", "-std=c++11", '-fvisibility=hidden']
_include_dirs = [pybind11.get_include(), "../src"]
_ext_modules = [
    Extension(
        name=__CUPLOADER_NAME__,
        sources=_sources,
        extra_compile_args=_extra_compile_args,
        include_dirs=_include_dirs,
    ),
]

setup(
    name=__CUPLOADER_NAME__,
    version=__CUPLOADER_VERSION__,
    author=__CUPLOADER_AUTHOR__,
    author_email=__CUPLOADER_AUTHOR_EMAIL__,
    description=__CUPLOADER_DESCRIPTION__,
    url=__CUPLOADER_URL__,
    license=__CUPLOADER_LICENSE__,
    ext_modules=_ext_modules,
    zip_safe=False,
)