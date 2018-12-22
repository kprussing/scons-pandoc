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
# Copyright (c) 2016-2018, Keith F. Prussing
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

class PanfluteNotFound(ToolPandocWarning):
    pass

SCons.Warnings.enableWarningClass(ToolPandocWarning)

def _detect(env):
    """Try to find Pandoc and :package:`panflute`
    """
    try:
        return env["PANDOC"]
    except KeyError:
        pass

    try:
        import panflute
    except ImportError:
        raise SCons.Errors.StopError(
                PanfluteNotFound, "Could not find :package:`panflute`"
            )

    pandoc = env.WhereIs("pandoc")
    if pandoc:
        return pandoc

    raise SCons.Errors.StopError(
            PandocNotFound, "Could not find Pandoc"
        )


def _scanner(node, env, path, arg=None):
    """ Attempt to scan the final target for images and bibliographies

    In Pandoc flavored MarkDown, the only "included" files are the
    images and the bibliographies.  We need to tell SCons about these,
    but we don't want to do this by hand.  To do this, we directly use
    Pandoc's json output and analyze the document tree for the images
    and the metadata for bibliographies.  We need to operate on the
    filtered syntax tree so we can get the final filtered version.  The
    logic should work on any input format Pandoc can translate into its
    AST.

    Note you must respect Pandoc's bibliography file rules.  The command
    line arguments will override files specified in the YAML block of
    the header file.

    This logic is primarily aimed at the MarkDown sources, but it should
    work with the other plain text sources too.  However, this is not
    rigorously tested.  For LaTeX sources, you should really just use
    the SCons builder to have the right thing done.

    """
    import panflute
    pandoc = _detect(env)
    # Grab the command SCons will run
    cmd = env.subst_target_source("$PANDOCCOM").split()
    for flag in ("-o", "--output"):
        try:
            cmd.remove(flag)
        except ValueError:
            # They specified the other flag
            pass

    # Add the sources to the command and specify JSON output
    cmd.extend([str(x) for x in node.sources])
    cmd.extend(["-t", "json"])
    proc =  subprocess.Popen(cmd, stdout=subprocess.PIPE)
    doc = panflute.load(proc.stdout)

    def walk(src):
        """Walk the tree and find images and bibliographies
        """
        if isinstance(src, panflute.Image):
            return [src.url]
        else:
            tmp = [walk(y) for y in getattr(src, "content", [])]
            return [y for z in tmp for y in z if y]

    images = [x for x in walk(doc) if x]
    root = os.path.dirname(str(node))
    _path = lambda x: env.File(os.path.join(root, x))
    files = [_path(x) for x in images]

    bibs = doc.metadata.content.get("bibliography", [])
    if bibs:
        files.extend([_path(x.text) for x
                      in getattr(bibs, "content", [bibs])])

    # print("{0!s}: {1!s}".format(node, [str(x) for x in files]))
    return files


_builder = SCons.Builder.Builder(
        action = SCons.Action.Action("$PANDOCCOM", "$PANDOCCOMSTR"),
        target_scanner = SCons.Scanner.Scanner(_scanner),
    )


def generate(env):
    """Add the Builders and construction variables to the Environment
    """
    env["PANDOC"] = _detect(env)
    command = "$PANDOC $PANDOCFLAGS -o ${TARGET.file} ${SOURCES.file}"
    env.SetDefault(
            # Command line flags.
            PANDOCFLAGS = SCons.Util.CLVar("--standalone"),

            # Commands.
            PANDOCCOM = command,
            PANDOCCOMSTR = "",

        )
    env["BUILDERS"]["Pandoc"] = _builder
    return


def exists(env):
    return _detect(env)

