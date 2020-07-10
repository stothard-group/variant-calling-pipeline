#!/usr/bin/env python3
import os
import sys
from shutil import which

## This script checks if we are working on computecanada and will load the appropriate modules.
## Otherwise, it will try to install programs with pip



def is_tool(toolname):
    """
    Check whether `toolname` is on PATH and marked as executable
    :param toolname: name of tool
    :return: 'toolname' is not None
    """
    return which(toolname) is not None

configfile = sys.argv[1]

host = os.popopen('hostname').read()
host = host.rstrip()

if host.endswith("computecanada.ca"):
    cc = True
else:
    cc = False
    
if cc:
    pass
else:
    check_fastqc = is_tool(fastqc)
    if not check_fastqc:
        print("FastQC does not appear to be installed in the path")
    