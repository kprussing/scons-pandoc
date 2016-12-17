#!/usr/bin/env python
# coding=utf-8

import os
import sys

def makedirs(target, source, env):
    """Prepare the user .scons directory

    We need to make sure the ~/.scons/site_scons/site_tools path exists.

    """
    if not os.path.exists(str(target[0])):
        os.makedirs(str(target[0]))

    return


def symlink(target, source, env):
    """Create a symlink.
    """
    srcpath = os.path.realpath(str(source[0]))
    os.symlink(srcpath, str(target[0]))
    return


toolsdir = os.path.join(
        os.path.expanduser("~"), ".scons", "site_scons", "site_tools"
    )

env = Environment()

source = "pandoc.py"
env.Install(toolsdir, source)
env.Alias("install", toolsdir)

if sys.platform not in ("win32", "cygwin") or sys.version_info > (3,2):
    target = os.path.join(toolsdir, source)
    env.AppendUnique(BUILDERS={"symlink" : Builder(action=symlink)})
    Mkdir(toolsdir)
    develop = env.symlink(target, source)
    env.Alias("develop", develop)

