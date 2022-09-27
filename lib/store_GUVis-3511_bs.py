# -*- coding: utf-8 -*-

import os, re, logging, pyodbc, csv
from datetime import datetime
from shutil import move

_log = logging.getLogger("uvsync")

def store(ctx, connection_string):
    
    # Function used to read and store data in downloaded UV log files for a speciffic instrument.
    # The instrument and station info is stored in the ctx (UVSyncContext) parameter
    
    connection = None

    try:        
        connection = pyodbc.connect(connection_string, autocommit = False)
        
        # The files to read and store in the database has been added to the ctx.sync_files 
        # list earlier by the validate function
        for file in ctx.sync_files:
            try:
                _log.info("Storing data from file " + str(file))
                with file.open() as fd:
                    # Call the 'store_file_fast' function to store a speciffic file
                    store_file_fast(connection, fd, ctx)
                
                # Move the stored file from the work directory to the outbox directory
                file_date = re.sub('GUV_[0-9]*_C_([0-9]*).csv', r'\1', file.name)
                file_year = '20' + file_date[0] + file_date[1]
                outdir = ctx.directory_outbox / ctx.station_name / file_year / str(ctx.channel_count)
                if not os.path.exists(outdir):
                    os.makedirs(outdir, exist_ok = True)
                fout = outdir / file.name
                _log.info("Moving from " + str(file) + " to " + str(fout))
                move(file, fout)

                # If everything went well, commit the data inserted to the database
                _log.info("Committing data from file " + str(fout))
                connection.commit()

            except Exception as ex:
                # Move the stored file from the work directory to the failed directory
                _log.info("Rolling back data from file " + str(file))
                # Discard any changes made to the database for this file
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
    
    # Function used to read and store a speciffic UV log file
    
    line_count = 0

    # Read the csv file line by line
    csv_reader = csv.reader(fd, delimiter=',')
    cursor = connection.cursor()
    cursor.fast_executemany = False

    for row in csv_reader:

        line_count += 1

        # Skip the first line (header)
        if line_count == 1:
            continue

        # Insert any rows with BioShadeMode 'P' or 'Z'
        if row[28] == 'P' or row[28] == 'Z':
            dt = datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")
            
            cursor.execute('exec insert_measurement2 ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?', (
                ctx.station_id, ctx.instrument_id, ctx.principal, dt,
                row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17],
                row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[30], row[29]
            ))
    
    _log.info("A total of %d lines processed" % (line_count-1))

def store_file_fast(connection, fd, ctx):
    
    # Function used to read and store a speciffic UV log file using batch insert for speed
    
    # Cache list to preload parameters into memory
    sqlparams = []

    line_count = 0

    # Read the csv file line by line
    csv_reader = csv.reader(fd, delimiter=',')    

    for row in csv_reader:

        line_count += 1

        # Skip the first line (header)
        if line_count == 1:
            continue

        # Cache any rows with BioShadeMode 'P' or 'Z'
        if row[28] == 'P' or row[28] == 'Z':
            dt = datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")
            t = (ctx.station_id, ctx.instrument_id, ctx.principal, dt,
                row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17],
                row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[30], row[29])
            sqlparams.append(t)

    # Insert rows as a batch job
    if len(sqlparams):
        cursor = connection.cursor()
        cursor.fast_executemany = True
        cursor.executemany('exec insert_measurement2 ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?', sqlparams)

    _log.info("A total of %d lines processed" % (line_count-1))
    _log.info("A total of %d lines inserted/updated" % (len(sqlparams)))