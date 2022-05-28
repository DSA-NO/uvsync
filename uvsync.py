# -*- coding: utf-8 -*-

import os, sys, pyodbc, configparser, pidfile
import uvsync_log
from pathlib import Path
from uvsync_context import UVSyncContextException, UVSyncContext
from datetime import date
from ftplib import FTP, error_perm

# Exit codes for this program
class ExitStatus: Success, Running, Error = range(3)

def main(log):
    
    # Main function for verifying and storing downloaded UV log files in the database    

    config = None
    connection_string = None
    uvsync_directory = None
    connection = None    

    try:
        script_dir = Path( __file__ ).parent.absolute()
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
            for station in cursor.fetchall():
                stations.append(station)
        finally:
            if connection is not None:
                connection.close()    

        # Create formatted date string of today, used later to check if a file is from today or not
        currdate = date.today().strftime("%y%m%d")

        # Call the 'handle_station' function for each station
        for station in stations:            
            handle_station(log, station, currdate)
    
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
    
def handle_station(log, station, currdate):
    
    # Function used to download UV log files from a speciffic station
    
    try:
        log.info("Retrieving files for station %s" % station.label)
        log.info("Logging in to host %s as %s" % (station.ftp_host, station.ftp_user))

        # Open FTP connection
        with FTP(station.ftp_host) as ftp:                
            ftp.login(user=station.ftp_user, passwd=station.ftp_password)            
            
            log.info("Set FTP passive mode: %d" % station.ftp_passive_mode)
            ftp.set_pasv(station.ftp_passive_mode)

            # Change local and remote directory
            if station.ftp_remote_dir:
                log.info("Changing remote directory to %s" % station.ftp_remote_dir)
                ftp.cwd(station.ftp_remote_dir)                
            if station.ftp_local_dir:
                log.info("Changing local directory to %s" % station.ftp_local_dir)
                os.chdir(station.ftp_local_dir)                

            # Get a list of remote files
            files = ftp.nlst()            
            for file in files:
                # Call the 'handle_file' function for each UV log file
                if file.find("_C_") != -1:
                    handle_file(log, ftp, file, currdate)                

    except Exception as ex:
        log.error(str(ex), exc_info=True) 

def handle_file(log, ftp, file, currdate):
    
    # Function used to download a speciffic UV log file using FTP
    
    try:
        log.info("Transfering remote file %s" % file)
        # Create a new file locally
        with open(file, 'wb') as f:        
            # Set up a callback function to receive blocks of data from FTP
            def callback(data):
                f.write(data)

            # Start downloading the file
            ftp.retrbinary("RETR %s" % file, callback)                    

            # Check if downloaded file is from today, if not, try to delete it on the remote machine
            filedate = file.split("_")[3]
            filedate = filedate.split(".")[0]                
            if filedate != currdate:
                try:
                    log.info("Deleting old remote file %s" % file)
                    ftp.delete(file)
                except:
                    log.error("Unable to delete old remote file %s" % file)
    except error_perm as ep:
        log.error("File permission error " + str(ep)) 
        if os.path.isfile(file):
            os.remove(file)
    except Exception as ex:
        log.error(str(ex), exc_info=True) 
        

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
