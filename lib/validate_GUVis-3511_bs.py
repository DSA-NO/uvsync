# -*- coding: utf-8 -*-

import logging, csv
from datetime import datetime
from shutil import move

_log = logging.getLogger("uvsync")

class UVSyncValidateGUVis3511BSException(Exception):
    ''' '''
    pass

def validate(ctx):
    ''' '''              

    try:
        work_files = ctx.directory_work.glob(ctx.match_expression)

        for file in work_files:
            try:
                _log.info("Validating data from file " + str(file))                
                with file.open() as fd:            
                    validate_file(fd, ctx)
                _log.info("Adding " + str(file) + " to sync list")
                ctx.sync_files.append(file)

            except UVSyncValidateGUVis3511BSException as ex:
                _log.info("[FAILED] " + str(ex)) 
                fout = ctx.directory_failed / file.name
                _log.info("Storing failed file " + str(file) + " as " + str(fout))  
                move(file, fout)
            except Exception as ex:
                _log.error("[FAILED]" + str(ex), exc_info=True)                 
                fout = ctx.directory_failed / file.name
                _log.info("Storing failed file " + str(file) + " as " + str(fout))  
                move(file, fout)

    except Exception as ex:
        _log.error(str(ex), exc_info=True) 

def validate_file(fd, ctx):
    ''' '''
    line_count = 0

    csv_reader = csv.reader(fd, delimiter=',')    

    for row in csv_reader:

        line_count += 1

        if line_count == 1:
            continue        

        ncol = len(row)
        if ncol != 32:
            raise UVSyncValidateGUVis3511BSException("Number of columns is wrong, got " + str(ncol) + ", should be 32")

        if row[0] != '3':
            raise UVSyncValidateGUVis3511BSException("Mode is wrong, got " + str(row[0]) + ", should be 3")

        try:
            dt = datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")        
        except Exception:
            raise UVSyncValidateGUVis3511BSException("Invalid datetime on line " + str(line_count))

