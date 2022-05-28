# -*- coding: utf-8 -*-

import os, sys, pyodbc, configparser, pidfile
import uvsync_log
from pathlib import Path
from uvsync_ftp import UVSyncFTPException, UVSyncFTP
from uvsync_context import UVSyncContextException, UVSyncContext
from datetime import date

# Exit codes for this program
class ExitStatus: Success, Running, Error = range(3)

def main(log):
    
    # Main function for verifying and storing downloaded UV log files in the database    

    config = None
    connection_string = None
    uvsync_directory = None
    connection = None    

    try:
        script_dir = Path(__file__).parent.absolute()
        log.info("Using script directory: %s" % script_dir)         

        config_file = script_dir / "config.ini"        
        if not config_file.exists():
            raise Exception("No config file found (%s)" % config_file)
        log.info("Using config file: %s" % config_file) 

        config = configparser.ConfigParser()
        config.read(config_file)
        
        connection_string = config['General']['connection_string']
        log.info("Connection_string loaded") 
        
        uvsync_directory = config['General']['uvsync_directory']
        log.info("Using uvsync directory: " + uvsync_directory)
        
        # Create uvsync directories if the don't already exists
        log.info("Creating directories under %s" % uvsync_directory)
        directory_inbox = Path(uvsync_directory) / "inbox"
        directory_work = Path(uvsync_directory) / "work"
        directory_outbox = Path(uvsync_directory) / "outbox"
        directory_failed = Path(uvsync_directory) / "failed"

        os.makedirs(directory_inbox, exist_ok = True)
        os.makedirs(directory_work, exist_ok = True)
        os.makedirs(directory_outbox, exist_ok = True)
        os.makedirs(directory_failed, exist_ok = True)
        
    except Exception as ex:
        log.error(str(ex), exc_info=True)
        return ExitStatus.Error    
    
    try:                     
        # List to store active stations from the database
        stations = []

        try:
            # Get active stations from the database            
            connection = pyodbc.connect(connection_string, autocommit = False)
            cursor = connection.cursor()
            cursor.execute("exec select_station_infos")
            for station_info in cursor.fetchall():
                log.info("Creating station %d|%s" % (station_info.id, station_info.label))
                station = UVSyncFTP(station_info, uvsync_directory)                
                stations.append(station)
        finally:
            if connection is not None:
                connection.close()    

        # Create formatted date string of today, used later to check if a file is from today or not
        currdate = date.today().strftime("%y%m%d")

        # Call the download function for each station
        for station in stations:            
            station.download(log, currdate)            
    
    except UVSyncFTPException as ex:
        log.error(str(ex))
        return ExitStatus.Error
    except Exception as ex:
        log.error(str(ex), exc_info=True)
        return ExitStatus.Error    
    
    try:                                    
        sync_contexts = []        

        # Get all active instruments from the database and store them as a list of contexts
        try:
            connection = pyodbc.connect(connection_string, autocommit = False)
            cursor = connection.cursor()
            cursor.execute("exec select_instrument_contexts")
            for instrument in cursor.fetchall():
                log.info("Creating sync context for instrument %d|%s" % (instrument.instrument_id, instrument.instrument_name))
                ctx = UVSyncContext(instrument, uvsync_directory)
                sync_contexts.append(ctx)
        finally:            
            if connection is not None:
                connection.close()        

        # Execute the fetch function for each instrument
        for ctx in sync_contexts:
            log.info("Fetching data for instrument %d|%s" % (ctx.instrument_id, ctx.instrument_name))
            ctx.fetch_module.fetch(ctx) # run in parallel

        # Execute the validate function for each instrument
        for ctx in sync_contexts:
            log.info("Validating data for instrument %d|%s at station %s" % (ctx.instrument_id, ctx.instrument_name, ctx.station_name))
            ctx.validate_module.validate(ctx) # run in parallel        

        # Execute the store function for each instrument
        for ctx in sync_contexts:
            log.info("Storing data for instrument %d|%s for station %s" % (ctx.instrument_id, ctx.instrument_name, ctx.station_name))
            ctx.store_module.store(ctx, connection_string) # run in parallel        
    
    except UVSyncContextException as ex:
        log.error(str(ex))
        return ExitStatus.Error
    except Exception as ex:
        log.error(str(ex), exc_info=True)
        return ExitStatus.Error
    
    return ExitStatus.Success

if __name__ == '__main__':
        
    try:
        with pidfile.PIDFile():
            log = uvsync_log.create_log("uvsync")   
            log.info("=========== START UVSYNC ===========")
            status = main(log)
            log.info("=========== END UVSYNC ===========")
            sys.exit(status)
    except pidfile.AlreadyRunningError:
        print('uvsync is already running')
        sys.exit(ExitStatus.Running)
    except Exception as ex:            
        print(str(ex))    
        sys.exit(ExitStatus.Error)    
