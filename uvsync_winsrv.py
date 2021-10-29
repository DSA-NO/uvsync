# -*- coding: utf-8 -*-

import sys, datetime, subprocess, servicemanager
from pathlib import Path

import win32event
from winsrv import WinSrv
from uvsync_win32 import get_registry_value

_registry_path = r"SOFTWARE\uvsync"

class UVSyncWinSrv(WinSrv):
    ''' '''
    _svc_name_ = "UVSync"
    _svc_display_name_ = "UVSync service"
    _svc_description_ = "Synchronization of UVNet station data"

    def start(self):
        ''' '''
        d = get_registry_value(_registry_path, "bindir")
        if d is None:
            servicemanager.LogMsg(servicemanager.EVENTLOG_ERROR_TYPE, 0xF000, ('UVSync: Unable to get registry key: bindir', ''))
            return

        sf = get_registry_value(_registry_path, "sync_frequency")
        if sf is None:
            servicemanager.LogMsg(servicemanager.EVENTLOG_ERROR_TYPE, 0xF000, ('UVSync: Unable to get registry key: sync_frequency', ''))
            return

        self.bindir = Path(d)
        self.sync_frequency = int(sf)
        self.isrunning = True
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, 0xF000, ('UVSync starting', ''))

    def stop(self):
        ''' '''
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, 0xF000, ('UVSync stopping', ''))
        self.isrunning = False

    def main(self):
        ''' '''
        try:
            while self.isrunning:
                start_time = datetime.datetime.now()
                try:
                    uvftp = self.bindir / "uvftp.py"
                    cp = subprocess.run(["python.exe", str(uvftp)])                
                    if cp.returncode == 0:
                        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, 0xF000, ('UVFTP success', ''))
                    elif cp.returncode == 1:                    
                        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, 0xF000, ('UVFTP was already running', ''))
                    else:
                        servicemanager.LogMsg(servicemanager.EVENTLOG_ERROR_TYPE, 0xF000, ('UVFTP error code: ' + str(cp.returncode), ''))
                except Exception as ex:
                    servicemanager.LogMsg(servicemanager.EVENTLOG_ERROR_TYPE, 0xF000, ('UVFTP failed to run: ' + str(ex), ''))

                try:                    
                    uvsync = self.bindir / "uvsync.py"
                    cp = subprocess.run(["python.exe", str(uvsync)])                
                    if cp.returncode == 0:
                        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, 0xF000, ('UVSync success', ''))
                    elif cp.returncode == 1:                    
                        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, 0xF000, ('UVSync was already running', ''))
                    else:
                        servicemanager.LogMsg(servicemanager.EVENTLOG_ERROR_TYPE, 0xF000, ('UVSync error code: ' + str(cp.returncode), ''))
                        
                except Exception as ex:
                    servicemanager.LogMsg(servicemanager.EVENTLOG_ERROR_TYPE, 0xF000, ('UVSync failed to run: ' + str(ex), ''))
                
                end_time = datetime.datetime.now()
                delta = (end_time - start_time)
                sleep_sub = delta.total_seconds()                         
                sleep_time = self.sync_frequency - int(sleep_sub)
                if sleep_time < 0:
                    sleep_time = 0
                #servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, 0xF000, ('Sleeping for ' + str(sleep_time), ''))                
                if win32event.WaitForSingleObject(self.hWaitStop, sleep_time * 1000) == win32event.WAIT_OBJECT_0: 
                    break

        except Exception as ex:
                servicemanager.LogMsg(servicemanager.EVENTLOG_ERROR_TYPE, 0xF000, ('UVSync exception: ' + str(sys.exc_info()), ''))

if __name__ == '__main__':
    ''' '''
    UVSyncWinSrv.parse_command_line()