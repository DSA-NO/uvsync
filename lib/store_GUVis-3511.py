# -*- coding: utf-8 -*-

import os, re, logging, pyodbc, csv
from datetime import datetime
from shutil import move

_log = logging.getLogger("uvsync")

def store(ctx, connection_string):

    # Function used to read and store data in downloaded UV log files for a speciffic instrument.
    # The instrument and station info is stored in the ctx (UVSyncContext) parameter.
    # See store_GUVis-3511_bs.py for more comments

    connection = None

    try:        
        connection = pyodbc.connect(connection_string, autocommit = False)        
        
        for file in ctx.sync_files:
            try:
                _log.info("Storing data from file " + str(file))                
                with file.open() as fd:            
                    store_file_fast(connection, fd, ctx)
                
                file_date = re.sub('GUV_[0-9]*_C_([0-9]*).csv', r'\1', file.name)
                file_year = '20' + file_date[0] + file_date[1]
                outdir = ctx.directory_outbox / ctx.station_name / file_year
                if not os.path.exists(outdir):
                    os.makedirs(outdir, exist_ok = True)
                fout = outdir / file.name                
                _log.info("Moving from " + str(file) + " to " + str(fout))
                move(file, fout)

                _log.info("Committing data from file " + str(fout))
                connection.commit()

            except Exception as ex:
                _log.info("Rolling back data from file " + str(file))
                connection.rollback() 
                _log.error(str(ex), exc_info=True) 
                fout = ctx.directory_failed / file.name
                _log.info("Storing failed file " + str(file) + " as " + str(fout))  
                move(file, fout)

    except Exception as ex:
        _log.error(str(ex), exc_info=True)    
    finally:
        if connection is not None:
            connection.close()

def store_file(connection, fd, ctx):
    
    line_count = 0

    csv_reader = csv.reader(fd, delimiter=',')   
    cursor = connection.cursor() 
    cursor.fast_executemany = False

    for row in csv_reader:

        line_count += 1

        if line_count == 1:
            continue        

        dt = datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")
        
        cursor.execute('exec insert_measurement2 ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?', (
            ctx.station_id, ctx.instrument_id, ctx.principal, dt,
            row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], 
            row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[28], row[27]
        ))
    
    _log.info("A total of %d lines processed" % (line_count-1))

def store_file_fast(connection, fd, ctx):
        
    sqlparams = []

    line_count = 0
    
    csv_reader = csv.reader(fd, delimiter=',')

    for row in csv_reader:

        line_count += 1

        if line_count == 1:
            continue
        
        dt = datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")

        t = (ctx.station_id, ctx.instrument_id, ctx.principal, dt,
            row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17],
            row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[28], row[27])
        sqlparams.append(t)

    if len(sqlparams):
        cursor = connection.cursor()
        cursor.fast_executemany = True
        cursor.executemany('exec insert_measurement2 ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?', sqlparams)

    _log.info("A total of %d lines processed" % (line_count-1))
    _log.info("A total of %d lines inserted/updated" % (len(sqlparams)))

