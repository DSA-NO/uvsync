# -*- coding: utf-8 -*-

import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

def create_log(name):
    
    # Create a logger object and save the log file under %PUBLIC%\uvnet.
    # On Windows the %PUBLIC% system variable typically refers to "C:\Brukere\Felles".
    # Set up a rotating log so that a new log file is created after 1MB file size is reached, 
    # and store up to 5 backup log files
    
    # Create log object
    logfmt = '%(asctime)s [%(levelname)s](%(module)s:%(lineno)d) %(message)s'
    logging.basicConfig(level=logging.INFO, format=logfmt)
    uvlogger = logging.getLogger(name)

    # Create logfile path
    script_dir = Path(__file__).parent.absolute()    
    logfile = name + ".log"
    logpath = script_dir / logfile    

    # Create rotating log
    handler = RotatingFileHandler(logpath, maxBytes=1000000, backupCount=5)
    formatter = logging.Formatter(logfmt)
    handler.setFormatter(formatter)
    uvlogger.addHandler(handler)    
    return uvlogger
