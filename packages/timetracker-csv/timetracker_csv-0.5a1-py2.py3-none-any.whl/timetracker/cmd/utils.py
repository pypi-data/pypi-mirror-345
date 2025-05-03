""" Common functions for commands"""

__copyright__ = 'Copyright (C) 2025-present, DV Klopfenstein, PhD. All rights reserved'
__author__ = "DV Klopfenstein, PhD"

from os.path import exists
from timetracker.msgs import str_init
from timetracker.msgs import str_reinit


def run_strinit(fcfg_project, fcfg_global=None, dirhome=None):
    """Check for existance of both local and global config to see if init is needed"""
    exist_glb = exists(fgcfg)
    if (exist_loc := exists(fcfg_project)) and exist_glb:
        return False
    #### trk projects does not need an initialized
    ####if not exist_loc:
    ####    print(str_init(fcfg_project))
    ####elif not exist_glb:
    elif not exist_glb:
        print(f'Global config, {fgcfg} not found')
        print(str_reinit())
    return True

# Copyright (C) 2025-present, DV Klopfenstein, PhD. All rights reserved
