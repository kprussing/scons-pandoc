Pandoc Support for SCons
========================

Basics
------

This goal of this project is to add support for Pandoc_ to SCons_
through the tool plugin system.  Once installed, to use the tool simply
add

    env = Environment(tools=["pandoc"])

to your ``SConstruct``.

Installation
------------

To install, simply copy the top of this project to
``site_scons/site_tools`` in your project directory, or you can place it
in you home directory under ``.scons/site_scons/site_tools``.  For more
details, check the `user's guide`_.  Alternatively, you can just run
``scons install`` and have it installed.

Hacking
-------

If you are on a Unix like system or a recent version of Windows and have
SCons running under Python 3.2 or newer, you can run ``scons develop``
to create the appropriate symlink.

.. _SCons: http://www.scons.org
.. _Pandoc: http://www.pandoc.org
.. _`user's guide`: http://scons.org/doc/production/HTML/scons-user.html#idm139837640082624

