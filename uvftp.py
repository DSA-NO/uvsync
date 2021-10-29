# -*- coding: utf-8 -*-

import os, sys, logging, pyodbc
from pathlib import Path
import uvsync_log
from datetime import date
from uvsync_win32 import get_registry_value
from ftplib import FTP, error_perm

_registry_path = r"SOFTWARE\uvsync"

class ExitStatus: Success, Running, Error = range(3)

def main(log):
    ''' '''                    
    try:             
        log.info("=========== START UVFTP ===========") 
        
        uvsync_directory = get_registry_value(_registry_path, "uvsync_directory")
        connection_string = get_registry_value(_registry_path, "connection_string")
        connection = None

        directory_inbox = Path(uvsync_directory) / "inbox"
        directory_work = Path(uvsync_directory) / "work"
        directory_outbox = Path(uvsync_directory) / "outbox"
        directory_failed = Path(uvsync_directory) / "failed"

        os.makedirs(directory_inbox, exist_ok = True)
        os.makedirs(directory_work, exist_ok = True)
        os.makedirs(directory_outbox, exist_ok = True)
        os.makedirs(directory_failed, exist_ok = True)

        stations = []

        try:
            connection = pyodbc.connect(connection_string, autocommit = False)
            cursor = connection.cursor()
        
            cursor.execute("exec select_station_infos")
            for station in cursor.fetchall():
                stations.append(station)
        finally:
            if connection is not None:
                connection.close()    

        currdate = date.today().strftime("%y%m%d")
        for station in stations:
            handle_station(log, station, currdate)
    
    except Exception as ex:
        log.error(str(ex), exc_info=True)
        return ExitStatus.Error    

    return ExitStatus.Success

def handle_station(log, station, currdate):
    try:
        log.info("Retrieving files for station %s" % station.label)
        log.info("Logging in to host %s as %s" % (station.ftp_host, station.ftp_user))

        with FTP(station.ftp_host) as ftp:                
            ftp.login(user=station.ftp_user, passwd=station.ftp_password)

            if station.ftp_remote_dir:
                log.info("Changing remote directory to %s" % station.ftp_remote_dir)
                ftp.cwd(station.ftp_remote_dir)                
            if station.ftp_local_dir:
                log.info("Changing local directory to %s" % station.ftp_local_dir)
                os.chdir(station.ftp_local_dir)                

            files = ftp.nlst()
            for file in files:
                if file.find("_C_") != -1:
                    handle_file(log, ftp, file, currdate)                

    except Exception as ex:
        log.error(str(ex), exc_info=True) 

def handle_file(log, ftp, file, currdate):
    try:
        log.info("Transfering remote file %s" % file)
        with open(file, 'wb') as f:        
            def callback(data):
                f.write(data)
            ftp.retrbinary("RETR %s" % file, callback)                    

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
    ''' '''   
    ''' singleton = ApplicationSingleton('Global\\01a05434-a665-43f2-950f-1e584497a17d') '''
    try:
        '''if not singleton.aquire():
            print("uvftp already running, exiting...")
            sys.exit(ExitStatus.Running) '''

        log = uvsync_log.create_log("uvftp")                                   
        exit_status = main(log)    
        sys.exit(exit_status)

    except Exception as ex:            
        print(str(ex))
    '''finally:
        singleton.release() '''