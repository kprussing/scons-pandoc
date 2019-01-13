Pandoc Support for SCons
========================

Introduction
------------

Pandoc_ is a handy command line tool that can convert plain text markup
files into different formats.  It does this by parsing the given input
files, representing them as an abstract syntax tree (AST), optionally
running the AST through one or more filters, and then writing the AST to
the desired output format.  In the process, Pandoc_ uses a collection of
files specified within the input document(s), via ``Image`` markup or in
a YAML metadata block, and command line flags.  Pandoc_ always process
the inputs to outputs even if the inputs have not changed.  For some
output formats, this is not a problem.  However, for others formats
(like PDF) this can cause unnecessary compilation that can potentially
be long.  Further, Pandoc_ does not know how to generate files from
sources unless it is handled with a filter.

A better solution is to use a build tool that understands dependency
scanning and can be extended to generate implicit dependencies.  SCons_
is a tool that fits this description.  If we can tell SCons_ what files
a Pandoc_ document depends on, we can let SCons_ handle what to build
when a document needs to be updated.  This exposes the full machinery of
SCons_ to generate graphics from raw input files to building a Pandoc_
document.  We could explicitly tell SCons_ the dependencies for each
document, but a more powerful method is to scan the AST itself and
provide the implicit dependency list to SCons_.

This goal of this project is to add support for Pandoc_ to SCons_
through the tool plugin system.

Usage
-----

Once installed, to use the tool simply add

    env = Environment(tools=["pandoc"])

to your ``SConstruct``.  Then, you specify a document via

   html = env.Pandoc("example.html", ["page1.md", "page2.md", "head.yaml"])

You can use the ``PANDOCFLAGS`` environment variable to add additional
flags to pass to Pandoc_ like filters, bibliography files, or even
metadata flags.

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
