# -*- coding: utf-8 -*-

import os, sys, importlib
from pathlib import Path

class UVSyncContextException(Exception):
    ''' '''
    pass

class UVSyncContext():
    ''' '''
    def __init__(self, instrument, uvsync_directory):
        ''' '''   
        self.instrument_id = int(instrument.instrument_id)
        self.station_id = int(instrument.station_id)
        if not instrument.instrument_name:
            raise UVSyncContextException("Missing label for instrument")
        self.instrument_name = instrument.instrument_name        
        if not instrument.station_name:
            raise UVSyncContextException("Missing label for station")
        self.station_name = instrument.station_name
        self.principal = instrument.principal        

        if not instrument.fetch_module:
            raise UVSyncContextException("Missing fetch_module for instrument " + self.instrument_name)
        self.fetch_module_name = instrument.fetch_module
        self.fetch_module = self.get_module(self.fetch_module_name)
        if self.fetch_module is None:
            raise UVSyncContextException("Unable to import fetch module " + self.fetch_module_name + " for instrument " + self.instrument_name)

        if not instrument.validate_module:
            raise UVSyncContextException("Missing validate_module for instrument " + self.instrument_name)                
        self.validate_module_name = instrument.validate_module                            
        self.validate_module = self.get_module(self.validate_module_name)
        if self.validate_module is None:
            raise UVSyncContextException("Unable to import validate module " + self.validate_module_name + " for instrument " + self.instrument_name)

        if not instrument.store_module:
            raise UVSyncContextException("Missing store_module for instrument " + self.instrument_name)                
        self.store_module_name = instrument.store_module                            
        self.store_module = self.get_module(self.store_module_name)
        if self.store_module is None:
            raise UVSyncContextException("Unable to import store module " + self.store_module_name + " for instrument " + self.instrument_name)

        if not instrument.match_expression:
            raise UVSyncContextException("Missing match_expression for instrument " + self.instrument_name)                
        self.match_expression = instrument.match_expression                                    
        if self.match_expression is None:
            raise UVSyncContextException("Invalid match expression for instrument " + self.instrument_name)

        self.directory_inbox = Path(uvsync_directory) / "inbox"
        self.directory_work = Path(uvsync_directory) / "work"
        self.directory_outbox = Path(uvsync_directory) / "outbox"
        self.directory_failed = Path(uvsync_directory) / "failed"

        os.makedirs(self.directory_inbox, exist_ok = True)
        os.makedirs(self.directory_work, exist_ok = True)
        os.makedirs(self.directory_outbox, exist_ok = True)
        os.makedirs(self.directory_failed, exist_ok = True)
            
        self.sync_files = []    

    def get_module(self, module_name):        
        ''' '''        
        return sys.modules[module_name] if module_name in sys.modules else importlib.import_module("lib." + module_name)