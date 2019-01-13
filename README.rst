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
in the `appropriate location`_ for your system.  For more details, check
the `SCons user's guide`_.  This tool requires Pandoc_ (obviously) and
panflute_.

Alternatively, you can add this project as a submodule to your git
project using

    git submodule add <url> site_scons/site_tools/pandoc

where ``<url>`` is the current URL of the project.

.. _SCons: http://www.scons.org
.. _`appropriate location`: https://github.com/SCons/scons/wiki/ToolsIndex#Install_and_usage
.. _Pandoc: http://www.pandoc.org
.. _`SCons user's guide`: http://scons.org/doc/production/HTML/scons-user.html
.. _panflute: https://pypi.org/project/panflute/
