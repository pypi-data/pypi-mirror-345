from setuptools import setup
from shein_api.__version__ import __version__

setup(
    name='shein_api',
    version=__version__,
    install_requires=[
        "requests>=2.26.0",
        "pycryptodome>=3.11.0"
    ],
    packages=[
        'shein_api',
        'shein_api.api',
        'shein_api.base',
    ],
    url='https://github.com/xie7654/shein_api',
    license='MIT',
    author='XIE JUN',
    author_email='xie765462425@gmail.com',
    description='Python wrapper for the SHEIN API',
)