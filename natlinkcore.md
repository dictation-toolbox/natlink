
# Natlinkcore 

## More Information
 Please refer to the README file in the project repository [https://github.com/dictation-toolbox/natlink](https://github.com/dictation-toolbox/natlink) for more information about natlink.

## Installing from PyPi
You can install from [The Python Package Index (PyPI)](https://pypi.org/) with 

pip install natlinkcore

## Building the Python Package Locally

The build happens through a powershell script.  You don't have to know much powershell.  

The package is built with [Flit](https://flit.pypa.io/).  The package will be produced in
dist/nalinkcore-x.y.tar.gz.  To install it `pip install dist/natlinkcore-x.y.tar.gz` replacing x.y with the version numbers.

To start a powershell from the command prompt, type `powershell`.

To build the package:

`build_natlinkcore` from powershell, which will run the the tests in natlinkcore/test, then build the the package.


To publish the package to [The Python Package Index (PyPI)](https://pypi.org/)

`publish_natlinkcore` from powershell.


You can use flit to install the package locally into site-packages using symbolic links, so you can test changes without reinstalling:

`flit install --symlink`


## Publishing checklist
Before you bump the version number in __init__.py and publish:
- Check the pyroject.toml file for package dependancies.  Do you need a specfic or newer version of
a dependancy such as dtactions?  Then add or update the version # requirement in dtactions.  
- don't publish if the tests are failing.   The `publish_natlinkcore` will prevent this, please don't work around it.



