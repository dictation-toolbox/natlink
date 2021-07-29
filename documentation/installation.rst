
Installation
============

Version 5.0.0 is a pippable version of Natlink, which is still in an experimental state.

We encourage Dragonfly developers to try this version. 

Natlink (for python 3) can be installed via pip (pypi), when Dragon is NOT running.

Start a :code:`Cmd` shell in elevated mode.

.. code:: shell

   $ pip install natlink
   $ natlinkconfig_cli

The configure program GUI seems not to work, so use the CLI (Command Line Interface).

Next type r ((re)Register)

.. code:: shell

   Config Natlink> r

Then restart :code:`Dragon`

When problems occur, you may need to manually remove natlink.pyd from the site-packages directory as indicated in the error message.

Next you can set the UserDirectory, with the `n` command.

.. code:: shell

   Config Natlink> n location-of-user-directory


