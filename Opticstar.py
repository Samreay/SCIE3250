# File explicitly based off work by Github user morefigs
# and his file found at https://github.com/morefigs/py-ic-imaging-control/blob/master/pyicic/IC_GrabberDLL.py

from ctypes import *
from ctypes.wintypes import HWND
import os

class OptistarDLL(object):
    HandlePtr = POINTER(Handle)
    dll_path = 'OSDS142MRT.dll'
    _dll = CDLL(dll_path)


    # This must be the first call to setup the camera. The iModel parameter specifies 
    # the camera model. iModel values: 0->DS-142M, 1->DS-142C.
    # If bStarView is true then the StarView window will be displayed. 
    # The hwOutVid is the window of the parent application, where real-time video will 
    # be displayed. The StarView window cannot be active at the same time as video preview.
    # The iRt value must be set to 0.
    init_library = _dll['OSDS142M_Initialize']
    init_library.restype = c_int
    init_library.argtypes = (c_int, c_bool, HWND, c_bool, c_int)

    # Always call this before exiting the application in order to clear the
    # resources used by the camera.
    exit_library = _dll['OSDS142M_Finalize']
    exit_library.restype = c_int
    exit_library.argtypes = None

class OpticstarControl(object):
	
    def __init__(self):
        err = OptistarDLL.init_library(0, False, 0, False, 0)
        if err != 0:
            raise Exception("Could not initialise the OSDS142MRT library")
		
    def __exit__(self, type, value, traceback):
        err = OptistarDLL.exit_library()
        if err != 0:
            raise Exception("Could not finalise the OSDS142MRT library")
