# -*- coding: utf-8 -*-

import logging, csv
from datetime import datetime
from shutil import move

_log = logging.getLogger("uvsync")

class UVSyncValidateGUVis3511BSException(Exception):
    '''
    Exception class used to report UVSyncValidateGUVis3511BS speciffic errors
    '''
    pass

def validate(ctx):
    '''
    Function used to validate data in downloaded UV log files for a speciffic instrument.
    The instrument and station info is stored in the ctx (UVSyncContext) parameter.
    Invalid files are moved to the 'failed' folder, valid files are added to the ctx.sync_list list
    '''              
    try:
        # Get filenames for this instrument
        work_files = ctx.directory_work.glob(ctx.match_expression)

        for file in work_files:
            try:
                _log.info("Validating data from file " + str(file))                

                # Open the file and call the 'validate_file' function for each speciffic file found
                with file.open() as fd:                        
                    validate_file(fd, ctx)

                _log.info("Adding " + str(file) + " to sync list")
                # Add filename to the list of files to be inserted into the database
                ctx.sync_files.append(file)

            except UVSyncValidateGUVis3511BSException as ex:
                # Validation failed, move file to 'failed' folder
                _log.info("[FAILED] " + str(ex)) 
                fout = ctx.directory_failed / file.name
                _log.info("Storing failed file " + str(file) + " as " + str(fout))  
                move(file, fout)
            except Exception as ex:
                # Some error occurred, move file to 'failed' folder
                _log.error("[FAILED]" + str(ex), exc_info=True)                 
                fout = ctx.directory_failed / file.name
                _log.info("Storing failed file " + str(file) + " as " + str(fout))  
                move(file, fout)

    except Exception as ex:
        _log.error(str(ex), exc_info=True) 

def validate_file(fd, ctx):
    '''
    Function used to validate a speciffic UV log file
    '''
    line_count = 0

    # Read csv file line by line
    csv_reader = csv.reader(fd, delimiter=',')    

    for row in csv_reader:

        line_count += 1

        # Skip first row (header)
        if line_count == 1:
            continue        

        # Check number of columns in this row
        ncol = len(row)
        if ncol != 32:
            raise UVSyncValidateGUVis3511BSException("Number of columns is wrong, got " + str(ncol) + ", should be 32")

        # Check Measurement Mode in this row
        if row[0] != '3':
            raise UVSyncValidateGUVis3511BSException("Mode is wrong, got " + str(row[0]) + ", should be 3")

        # Check for a valid date/time
        try:
            dt = datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")        
        except Exception:
            raise UVSyncValidateGUVis3511BSException("Invalid datetime on line " + str(line_count))

