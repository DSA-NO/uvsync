# -*- coding: utf-8 -*-

import logging, pyodbc, csv
from datetime import datetime
from shutil import move

_log = logging.getLogger("uvsync")

def store(ctx, connection_string):
    ''' '''          
    connection = None

    try:        
        connection = pyodbc.connect(connection_string, autocommit = False)
        cursor = connection.cursor()
        
        for file in ctx.sync_files:
            try:
                _log.info("Storing data from file " + str(file))                
                with file.open() as fd:            
                    store_file(cursor, fd, ctx)
                
                fout = ctx.directory_outbox / file.name
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

def store_file(cursor, fd, ctx):
    ''' '''
    line_count = 0

    csv_reader = csv.reader(fd, delimiter=',')    

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
