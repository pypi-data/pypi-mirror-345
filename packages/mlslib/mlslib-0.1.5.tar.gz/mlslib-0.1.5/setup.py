'''
This setup.py file is used to package the dslib library. It includes metadata such as the name, version, and author information.
The find_packages() function automatically discovers all packages and subpackages in the directory.
The install_requires list can be populated with any dependencies that the library requires.
The classifiers provide additional metadata about the package, such as the programming language version.
The URL field is optional and can point to the project's repository or documentation.
'''
from setuptools import setup, find_packages

setup(
    name='mlslib',
    version='0.1.5',
    packages=find_packages(),
    install_requires=[],
    description='A utility library for working data pipelines',
    author='Raj Jha',
    author_email='rjha4@wayfair.com',
    url='https://github.com/wayfair-sandbox/dslib',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)
