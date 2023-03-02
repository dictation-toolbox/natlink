Introduction
============
Natlink has been used to extend Dragon Naturally Speaking (Dragon) with Python modules. Many developers of extensions 
for Dragon find it more practical to develop and share extensions using Python than the built in Visual Basic macros of Dragon.

Similarly, many end users find it easier to  use Dragon extensions written in Natlink than to locate and install 
scripts using the built in Dragon scripting. However, an end user may have to edit or rename the occasional text file,
or run a command lind program `pip` to install a Python package.

End users interact with an extension with a Natlink grammar.  A grammar specifies what will 
happen when certain words are dictated with grammar rules. 

For example, a hypothetical grammar could have a very simple rule "american date today" which prints the current
date out in a format mm/dd/yyyy.

Grammars can be used to insert text boilerplate, operate the menus of programs, or otherwise control a computer.  
They can even be used to help write computer programs.

Using a Published Grammar
=========================


Installing a Published Grammar
==============================

Follow the instructions for the specific grammar or extension. If the author has published 
the package xyz to PyPI  https://pypi.org/  you will be able to install it with a command line 'pip install xyz'
in a command shell or powershell prompt and add the necessary lines to natlink.ini
(something like xyz=xyz).  

They might provide other instructions on installing the package with pip,
or just provide a python file for you to figure out what to deal with. In the case where they just provide you python files, 
the python files module must be placed in a folder listed in the directories section of natlink.ini. 
 


As an end user of Natlink, you may be never need to write your own grammar, and you won't need programming skills.  
You will need to Python packages and  grammars and perhaps do some small amount of configuration on your computer. 

Grammars are implemented as Python modules. A Python module is a single Python 
file which is identified with the ".py"
extension.  Natlink needs to know to load these Python modules.  This is done through 
the 
TODO insert hyperlink   configuration file natlink.ini.

natlink.ini has a [directories] setting that lists the directories (file folders) natlink loads grammars from.  
You can add as many as you need.

A line may look like
`name = directory`

The name on the left of the equals is just a one word descriptor, and natlink doesn't do much with the name. 
Sometimes confusingly they may the same or similar
as the directory on the right of the equals. 

The directory can be:
- the name of Python package you have installed.  Generally this is the easiest if someone has published a grammar 
as a Python package.
- a folder on your file system where you have placed the Python file OR 
where an extension will place Python files.  

In any case, natlink will load all the python code in all the directories listed in the natlink.ini config file.

It can be confusing becuase you might see two directories with similar names.  For example,
Vocola uses two directories in natlink.ini.  Natlink.ini will have two lines for Vocola:

[directories]
vocoladirectory = vocola2
vocolagrammarsdirectory = natlink_userdir\vocolagrammars

This is because vocola has a bunch of Python that needs to be loaded from the vocola2 Python package and
a bunch more Python that vocola itself creates at runtime and places in vocolagrammarsdirectory.  Some other 
natlink extensions do the same thing.  

 

