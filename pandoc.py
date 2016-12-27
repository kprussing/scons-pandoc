# coding=utf-8
from __future__ import unicode_literals, print_function

__doc__="""SCons.Tool.pandoc

The Tool specific initialization for the Pandoc document conversion
command line tool.

There normally shouldn't be any need to import this module directly.  It
will usually be imported through the generic SCons.Tool.Tool() selection
method.

"""

#
# Copyright (c) 2016, Keith F. Prussing
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
#     1. Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
# 
#     2. Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the following
#     disclaimer in the documentation and/or other materials provided
#     with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# Acknowledgements
# ----------------
#
# The format of this Tool is highly influenced by the JAL Tool on the
# ToolsForFools_ page from the SCons Wiki.
#
# .. ToolsForFools: https://bitbucket.org/scons/scons/wiki/ToolsForFools
#

import SCons.Action
import SCons.Builder
import SCons.Scanner
import SCons.Util

import json
import os
import subprocess

class ToolPandocWarning(SCons.Warnings.Warning):
    pass

class PandocNotFound(ToolPandocWarning):
    pass

SCons.Warnings.enableWarningClass(ToolPandocWarning)

def _detect(env):
    """Try to find Pandoc.
    """
    try:
        return env["PANDOC"]
    except KeyError:
        pass

    pandoc = env.WhereIs("pandoc")
    if pandoc:
        return pandoc

    raise SCons.Errors.StopError(
            PandocNotFound, "Could not find Pandoc"
        )

def _scanner(node, env, path, arg=None):
    """Scan the sources files for image dependencies.

    In Pandoc flavored MarkDown, the only "included" files are the
    images.  We need to tell SCons about these, but we don't want to do
    this by hand.  To do this, we directly use Pandoc's json output and
    analyze the document tree for the images.  This logic is primarily
    aimed at the MarkDown sources, but it should work with the other
    plain text sources too.  However, this is not rigorously tested.
    For LaTeX sources, you should really just use the SCons builder to
    have the right thing done.

    """
    import re
    pandoc = _detect(env)
    # if not os.path.exists(str(node)):
        # raise RuntimeError("{0:s} not found".format(node))

    tree = subprocess.check_output([pandoc, "-t", "json", str(node)])

    def walk(data):
        """Heavily borrowed from ``pandocfilters.walk``

        The major difference is we cannot throw out the lower parts of
        the tree because we need to down as low as possible to find an
        'Image' item.

        """
        if isinstance(data, list):
            tmp = [walk(x) for x in data]
            res = [x for x in tmp if x != []]

        elif isinstance(data, dict):
            res = []
            if "t" in data and re.match("Image", data["t"], re.I):
                value = data["c"] if "c" in data else []
                if len(value) == 2:
                    # Before pandoc 1.16
                    alt, [src, title] = value
                else:
                    attrs, alt, [src, title] = value

                # print(src)
                res.append(src)
            else:
                for key, value in data.items():
                    res.extend(walk(value))

        else:
            res = []

        return [x for x in res if x != []]


    data = json.loads(tree)
    root = os.path.dirname(str(node))
    deps = [x for l in walk(data) for x in l if x != []]
    # print(deps)
    files = [env.File(os.path.join(root, x)) for y in deps for x in y]
    # print(files)
    return files


_builder = SCons.Builder.Builder(
        action = SCons.Action.Action("$PANDOC_COM", "$PANDOC_COMSTR"),
        chdir = 1,
        source_scanner = SCons.Scanner.Scanner(_scanner)
    )


def generate(env):
    """Add the Builders and construction variables to the Environment
    """
    env["PANDOC"] = _detect(env)
    command = "$PANDOC $PANDOC_FLAGS -o ${TARGET.file} ${SOURCES.file}"
    env.SetDefault(
            # Command line flags.
            PANDOC_FLAGS = SCons.Util.CLVar("--standalone"),

            # Commands.
            PANDOC_COM = command,
            PANDOC_COMSTR = "",

        )
    env["BUILDERS"]["Pandoc"] = _builder
    return


def exists(env):
    return _detect(env)

