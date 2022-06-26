
# Natlinkcore 

## More Information
 Please refer to the README file in the project repository [https://github.com/dictation-toolbox/natlink](https://github.com/dictation-toolbox/natlink) for more information about natlink.

## Installing from PyPi
You can install from [The Python Package Index (PyPI)](https://pypi.org/) with 

pip install natlinkcore

## Building the Python Package Locally

The package is built with [Flit](https://flit.pypa.io/).

To build the package:

`flit build --format sdist`

To publish the package to [The Python Package Index (PyPI)](https://pypi.org/)

`flit publish --format sdist`


You can use flit to install the package locally into site-packages using symbolic links, so you can test changes without reinstalling:

`flit install -s`


You can use pip to install the locally built package into your Python's site-packages directory.

`pip install dist/natlinkcore`.





