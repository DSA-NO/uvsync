# -*- coding: utf-8 -*-

import sys, logging, pyodbc
import uvsync_log
from uvsync_context import UVSyncContextException, UVSyncContext
from uvsync_win32 import get_registry_value

_registry_path = r"SOFTWARE\uvsync"

class ExitStatus: Success, Running, Error = range(3)

def main(log):
    ''' '''        
    try:                            
        log.info("=========== START UVSYNC ===========")                 
        
        uvsync_directory = get_registry_value(_registry_path, "uvsync_directory")
        connection_string = get_registry_value(_registry_path, "connection_string")                
        connection = None
        sync_contexts = []        

        try:
            connection = pyodbc.connect(connection_string, autocommit = False)
            cursor = connection.cursor()
            
            cursor.execute("exec select_instrument_contexts")
            for instrument in cursor.fetchall():
                log.info("Creating sync context for instrument %s" % (instrument.instrument_name))
                ctx = UVSyncContext(instrument, uvsync_directory)
                sync_contexts.append(ctx)                                
        finally:            
            if connection is not None:
                connection.close()        
                    
        for ctx in sync_contexts:
            log.info("Fetching data for instrument %d|%s" % (ctx.instrument_id, ctx.instrument_name))
            ctx.fetch_module.fetch(ctx) # run in parallel

        for ctx in sync_contexts:
            log.info("Validating data for instrument %d|%s at station %s" % (ctx.instrument_id, ctx.instrument_name, ctx.station_name))
            ctx.validate_module.validate(ctx) # run in parallel        

        for ctx in sync_contexts:
            log.info("Storing data for instrument %d|%s for station %s" % (ctx.instrument_id, ctx.instrument_name, ctx.station_name))
            ctx.store_module.store(ctx, connection_string) # run in parallel
            
        log.info("Sync finished")
    
    except UVSyncContextException as ex:
        log.error(str(ex))
        return ExitStatus.Error
    except Exception as ex:
        log.error(str(ex), exc_info=True)
        return ExitStatus.Error
    
    return ExitStatus.Success
    
if __name__ == '__main__':
    ''' '''    
    ''' singleton = ApplicationSingleton('Global\\03e0118e-b38b-4171-be9a-f92dc94abd20') '''
    try:        
        '''if not singleton.aquire():
            print("uvsync already running, exiting...")
            sys.exit(ExitStatus.Running) '''

        log = uvsync_log.create_log("uvsync")   
        exit_status = main(log)
        sys.exit(exit_status)
        
    except Exception as ex:            
        print(str(ex))
    '''finally:
        singleton.release()'''