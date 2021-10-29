# -*- coding: utf-8 -*-

from win32event import CreateMutex, ReleaseMutex, WaitForSingleObject, WAIT_OBJECT_0
from win32file import CreateFile, CloseHandle
from win32con import GENERIC_READ, GENERIC_WRITE, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL
from win32api import GetLastError
from winerror import ERROR_ALREADY_EXISTS
from winreg import CreateKey, OpenKey, CloseKey, SetValueEx, QueryValueEx, HKEY_LOCAL_MACHINE, KEY_READ, KEY_WRITE, REG_SZ

'''class ApplicationSingleton():
    def __init__(self, identifier):
        self.handle = None
        self.identifier = identifier

    def aquire(self):    
        if self.handle:
            return True
        self.handle = CreateMutex(None, False, self.identifier)
        if self.handle == None:
            raise Exception("CreateMutex failed with code " + str(GetLastError()))
        if GetLastError() == ERROR_ALREADY_EXISTS:
            CloseHandle(self.handle)
            self.handle = None
            return False
        status = WaitForSingleObject(self.handle, 0)
        if status == WAIT_OBJECT_0:
            return True
        else:            
            CloseHandle(self.handle)
            self.handle = None
            return False

    def release(self): 
        if self.handle:       
            ReleaseMutex(self.handle)
            CloseHandle(self.handle) '''
        
def has_exclusive_access(filename):
    '''
    Check if we have exclusive access to a file
    '''
    try:
        handle = CreateFile(str(filename), GENERIC_READ | GENERIC_WRITE, 0, None, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, None)
        CloseHandle(handle)
    except:
        return False            
    return True

def set_registry_value_sz(regpath, name, value):
    '''
    Write a registry parameter
    '''
    try:
        CreateKey(HKEY_LOCAL_MACHINE, regpath)
        registry_key = OpenKey(HKEY_LOCAL_MACHINE, regpath, 0, KEY_WRITE)
        SetValueEx(registry_key, name, 0, REG_SZ, value)
        CloseKey(registry_key)
        return True
    except WindowsError:
        return False

def get_registry_value(regpath, name):
    '''
    Read a registry parameter
    '''
    try:
        registry_key = OpenKey(HKEY_LOCAL_MACHINE, regpath, 0, KEY_READ)
        value, regtype = QueryValueEx(registry_key, name)
        CloseKey(registry_key)
        return value
    except WindowsError:
        return None