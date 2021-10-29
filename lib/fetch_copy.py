# -*- coding: utf-8 -*-

import logging
from shutil import move
from uvsync_win32 import has_exclusive_access

_log = logging.getLogger("uvsync")

def fetch(ctx):
    ''' 
    Copy files from directory_inbox to directory_work filtered on expression match_expression
    '''    
    _log.info("Processing directory " + str(ctx.directory_inbox) + " with expression " + ctx.match_expression)
    
    ifiles = ctx.directory_inbox.glob(ctx.match_expression)
    ifiles_sorted = sorted(ifiles)

    for fin in ifiles_sorted:
        try:
            if not has_exclusive_access(fin):
                _log.info("Unable to aquire exclusive access to " + str(fin))
                continue            
            fwork = ctx.directory_work / fin.name[1:] if fin.name.startswith('A') else ctx.directory_work / fin.name            
            _log.info("Moving from " + str(fin) + " to " + str(fwork))
            move(fin, fwork)            
        except Exception as ex:
            _log.error(str(ex), exc_info=True)