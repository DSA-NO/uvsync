# -*- coding: utf-8 -*-

import socket
import win32serviceutil
import servicemanager
import win32event
import win32service


class WinSrv(win32serviceutil.ServiceFramework):
    # Base class to create windows service in Python
    _svc_name_ = 'WinSrv'
    _svc_display_name_ = 'WinSrv'
    _svc_description_ = 'Windows Service'

    @classmethod
    def parse_command_line(cls):
        # ClassMethod to parse the command line
        win32serviceutil.HandleCommandLine(cls)

    def __init__(self, args):
        # Constructor of the WinSrv
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        # Called when the service is asked to stop
        self.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        # Called when the service is asked to start
        self.start()
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def start(self):
        # Override to add logic before the start
        pass

    def stop(self):
        # Override to add logic before the stop
        pass

    def main(self):
        # Main class to be overridden to add logic
        pass

if __name__ == '__main__':
    
    WinSrv.parse_command_line()