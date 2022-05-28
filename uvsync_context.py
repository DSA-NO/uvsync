# -*- coding: utf-8 -*-

import sys, importlib
from pathlib import Path

class UVSyncContextException(Exception):
    
    # Exception class used to report UVSyncContext speciffic errors    
    pass

class UVSyncContext():
    
    # Define a class used to hold all relevant information needed to synchronize a speciffic instrument
    
    def __init__(self, instrument, uvsync_directory):
        
        # Constructor, initialize all member variables
        
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

        # Declare variables for all uvsync directories, and create them if they don't exist already
        self.directory_inbox = Path(uvsync_directory) / "inbox"
        self.directory_work = Path(uvsync_directory) / "work"
        self.directory_outbox = Path(uvsync_directory) / "outbox"
        self.directory_failed = Path(uvsync_directory) / "failed"        
            
        # List of files to store in the database, this list is filled by the validate module
        self.sync_files = []

    def get_module(self, module_name):        

        # Function used to load the fetch, validate and store modules for each instrument

        return sys.modules[module_name] if module_name in sys.modules else importlib.import_module("lib." + module_name)