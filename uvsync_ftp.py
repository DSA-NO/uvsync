# -*- coding: utf-8 -*-

import os
from pathlib import Path
from ftplib import FTP, error_perm

class UVSyncFTPException(Exception):
    
    # Exception class used to report UVSyncFTP speciffic errors    
    pass

class UVSyncFTP():
    
    # Define a class used to hold all relevant information needed to download from a station
    
    def __init__(self, station, uvsync_directory):
        
        # Constructor, initialize all member variables
        
        self.station_id = int(station.id)        
        if not station.label:
            raise UVSyncFTPException("Missing label for station")        
        self.station_name = station.label                

        if not station.ftp_host:
            raise UVSyncFTPException("Missing FTP host for station " + self.station_name)
        self.ftp_host = station.ftp_host        

        if not station.ftp_user:
            raise UVSyncFTPException("Missing FTP user for station " + self.station_name)
        self.ftp_user = station.ftp_user

        if not station.ftp_password:
            raise UVSyncFTPException("Missing FTP password for station " + self.station_name)
        self.ftp_password = station.ftp_password
        
        self.ftp_remote_dir = station.ftp_remote_dir        
        self.ftp_local_dir = station.ftp_local_dir        
        self.ftp_passive_mode = int(station.ftp_passive_mode)

        # Declare variables for all uvsync directories, and create them if they don't exist already
        self.directory_inbox = Path(uvsync_directory) / "inbox"
        self.directory_work = Path(uvsync_directory) / "work"
        self.directory_outbox = Path(uvsync_directory) / "outbox"
        self.directory_failed = Path(uvsync_directory) / "failed"

    def download(self, log, currdate):
        
        # Function used to download UV log files from a speciffic station
        
        try:
            log.info("Retrieving files for station %s" % self.station_name)
            log.info("Logging in to host %s as %s" % (self.ftp_host, self.ftp_user))

            # Open FTP connection
            with FTP(self.ftp_host) as ftp:                
                ftp.login(user=self.ftp_user, passwd=self.ftp_password)            
                
                log.info("Set FTP passive mode: %d" % self.ftp_passive_mode)
                ftp.set_pasv(self.ftp_passive_mode)

                # Change local and remote directory
                if self.ftp_remote_dir:
                    log.info("Changing remote directory to %s" % self.ftp_remote_dir)
                    ftp.cwd(self.ftp_remote_dir)                
                if self.ftp_local_dir:
                    log.info("Changing local directory to %s" % self.ftp_local_dir)
                    os.chdir(self.ftp_local_dir)                

                # Get a list of remote files
                files = ftp.nlst()            
                for file in files:
                    # Call the 'handle_file' function for each UV log file
                    if file.find("_C_") != -1:
                        self.__handle_file(log, ftp, file, currdate)                

        except Exception as ex:
            log.error(str(ex), exc_info=True) 

    def __handle_file(self, log, ftp, file, currdate):
        
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