from ctypes import *
from ctypes.wintypes import HWND
import os

class OpticstarDLL(object):
    dll_path = 'OSDS142MRT.dll'
    _dll = CDLL(dll_path)

    # This must be the first call to setup the camera. The iModel parameter specifies 
    # the camera model. iModel values: 0->DS-142M, 1->DS-142C.
    # If bStarView is true then the StarView window will be displayed. 
    # The hwOutVid is the window of the parent application, where real-time video will 
    # be displayed. The StarView window cannot be active at the same time as video preview.
    # The iRt value must be set to 0.
    # DLLDIR int OSDS142M_Initialize(int iModel, bool bOutVid, HWND hwOutVid, bool bStarView, int iRt);
    init_library = _dll['OSDS142M_Initialize']
    init_library.restype = c_int
    init_library.argtypes = (c_int, c_bool, HWND, c_bool, c_int)

    # Always call this before exiting the application in order to clear the
    # resources used by the camera.
    exit_library = _dll['OSDS142M_Finalize']
    exit_library.restype = c_int
    exit_library.argtypes = None

    # Shows or hides the StarView window.
    show_star_view = _dll['OSDS142M_ShowStarView']
    show_star_view.restype = c_int
    show_star_view.argtypes = (c_bool,)

    # Plays video preview if bPlay is true. The iBinningMode and iExposureTime
    # assign the binning mode and exposure time to used. The video is displayed inside
    # the Windows window specified in OSDS142M_Initialize(). The iExposureTime is in 
    # milliseconds. If iExposureTime is -1 then automatic exposure mode is used.
    # If bVideoPreview is false then no video is generated.
    video_preview = _dll['OSDS142M_VideoPreview']
    video_preview.restype = c_int
    video_preview.argtypes = (c_bool, c_int, c_int)

    # Captures an image according to the parameters. The iBinningMode value
    # should be one of the following:
    #--------------------------------------------------------------------------------------
    # Mode  Binning  Resolution  Data   Max   Monochrome  Bayer grid  Camera models
    #                            Width  FPS   or Colour   preserved?
    #--------------------------------------------------------------------------------------
    #  0     1x1     1360x1024  16-bit   ?      mono         no       DS-145M/C, DS-142M/C
    #  1     2x2      680x512   16-bit   ?      mono         no       DS-145M/C, DS-142M/C
    #  2     4x4      340x256   16-bit   ?      mono         no       DS-145M/C, DS-142M/C
    #  3     1x1     1360x1024   8-bit   ?      mono         no       DS-145M/C, DS-142M/C
    #  4     2x2      680x512    8-bit   ?      mono         no       DS-145M/C, DS-142M/C
    #  5     4x4      340x256    8-bit   ?      mono         no       DS-145M/C, DS-142M/C
    #
    # All binning modes output data to the application at 16 bits per pixel, even when
    # the camera operates in 8-bit modes (fast read-out).
    
    # Grabs an image in the specified binning mode and with the specified exposure
    # time. The exposure time, lExposureTime, must be in milliseconds and must be >= -1.
    # If the exposure is -1 then auto-exposure is used. If the video preview is 
    # playing, then this call will fail.
    # DLLDIR int OSDS142M_Capture(int iBinningMode, int iExposureTime);
    capture = _dll['OSDS142M_Capture']
    capture.restype = c_int
    capture.argtypes = (c_int, c_int)

    # The pbExposing flag returns true or false depending whether an exposure
    # is currently taking place or aborting. If an exposure is in progress, 
    # then pdwTimeRemaining returns the time remaining in milliseconds.
    is_exposing = _dll['OSDS142M_IsExposing']
    is_exposing.restypes = c_int
    is_exposing.argtypes = (POINTER(c_bool), POINTER(c_uint))

    # If an exposure takes place, it can be stopped by calling this function. 
    # Keep calling OSDS145M_IsExposing() in order to determine whether the exposure 
    # has been stopped.
    stop_exposure = _dll['OSDS142M_StopExposure']
    stop_exposure.restype = c_int
    stop_exposure.argtypes = None

    # Adds an offset to the raw data. This value is 0 by default but it can be set to
    # a 16-bit value that will be added to the raw data. All binning modes output
    # 16-bit values (even the 8-bit fast read-out modes).
    set_raw_offset = _dll['OSDS142M_SetRawOffset']
    set_raw_offset.restype = c_int
    set_raw_offset.argtypes = (c_ushort,)

    # Gain settings. Range: 1 - 1023.
    set_gain = _dll['OSDS142M_SetGain']
    set_gain.restype = c_int
    set_gain.argtypes = (c_ushort,)

    get_gain = _dll['OSDS142M_GetGain']
    get_gain.restype = c_int
    get_gain.argtypes = (POINTER(c_ushort),)

    # Various image settings. Range: 0 - 255.
    set_contrast = _dll['OSDS142M_SetContrast']
    set_contrast.restype = c_int
    set_contrast.argtypes = (c_ubyte,)
    
    get_contrast = _dll['OSDS142M_GetContrast']
    get_contrast.restype = c_int
    get_contrast.argtypes = (POINTER(c_ubyte),)

    set_black_level = _dll['OSDS142M_SetBlackLevel']
    set_black_level.restype = c_int
    set_black_level.argtypes = (c_ubyte,)
    
    get_black_level = _dll['OSDS142M_GetBlackLevel']
    get_black_level.restype = c_int
    get_black_level.argtypes = (POINTER(c_ubyte),)

    set_gamma = _dll['OSDS142M_SetGamma']
    set_gamma.restype = c_int
    set_gamma.argtypes = (c_ubyte,)
    
    get_gamma = _dll['OSDS142M_GetGamma']
    get_gamma.restype = c_int
    get_gamma.argtypes = (POINTER(c_ubyte),)

    set_saturation = _dll['OSDS142M_SetSaturation']
    set_saturation.restype = c_int
    set_saturation.argtypes = (c_ubyte,)
    
    get_saturation = _dll['OSDS142M_GetSaturation']
    get_saturation.restype = c_int
    get_saturation.argtypes = (POINTER(c_ubyte),)
    
    # Auto Exposure Target value. Range: 0 - 255.
    set_ae_target = _dll['OSDS142M_SetAeTarget']
    set_ae_target.restype = c_int
    set_ae_target.argtypes = (c_ubyte,)
    
    get_ae_target = _dll['OSDS142M_GetAeTarget']
    get_ae_target.restype = c_int
    get_ae_target.argtypes = (POINTER(c_ubyte),)
    


    # Gets a region of a captured native image as exported by the CCD camera to the 
    # computer. It returns image data from the last OSDS142M_Capture() call. The 
    # application must allocate the memory for pvNativeBuf. The memory to be allocated
    # by the application should be (iWidth * iHeight * 2). The raw image data is
    # always in 16-bits per pixel format even when the camera has captured in an 8-bit 
    # mode. As soon as the image data enters the computer, it is converted in 16-bit 
    # (native) format. The maximum buffer size should be (1360 * 1024 * 2).
    # The iX, iY, iWidth and iHeight  coordinates are in pixels and they must be 
    # dividable by the pixel binning mode. For example, if 2x2 binning has been used 
    # in OSDS142M_Capture() then all these parameters must be dividable by 2 and so on.
    # DLLDIR int OSDS142M_GetRawImage(int iX, int iY, int iWidth, int iHeight, void *pvRawBuf);
    get_raw_image = _dll['OSDS142M_GetRawImage']
    get_raw_image.restype = c_int
    get_raw_image.argtypes = (c_int, c_int, c_int, c_int, POINTER(c_short))

    # Turns the raw data upside down.
    # DLLDIR int OSDS142M_InvertRawImage(int iWidth, int iHeight, void *pvRawBuf);
    invert_raw_image = _dll['OSDS142M_InvertRawImage']
    invert_raw_image.restype = c_int
    invert_raw_image.argtypes = (c_int, c_int, POINTER(c_short))
    

class OpticstarControl(object):
	
    def __init__(self, logging=False):
        """
        Initializes the library. Star view for preview not capture
        """
        self.logging = logging
        err = OpticstarDLL.init_library(0, False, 0, False, 0)
        if err != 0:
            raise Exception("Could not initialise the OSDS142MRT library. Error code %d" % err)
        elif self.logging:
            print("Library initialised without error")

    def closeLibrary(self):
        if self.logging: print("Closing library")
        err = OpticstarDLL.exit_library()
        if err != 0:
            raise Exception("Could not finalise the OSDS142MRT library")
        elif self.logging: print("Closed library")
        
    def __exit__(self, type, value, traceback):
        self.closeLibrary()

    def showStarView(self):
        """
        Shows the star view preview
        """
        err = OpticstarDLL.show_star_view(True)
        if err != 0:
            raise Exception("Could not show Star View")

    def playVideoPreview(self):
        """
        Starts the video preview
        """
        err = OpticstarDLL.video_preview(True, 0, -1)
        if err != 0:
            raise Exception("Could not start video preview")
        
    def stopVideoPreview(self):
        """ Stops the video preview """
        err = OpticstarDLL.video_preview(False, 0, -1)
        if err != 0:
            raise Exception("Could not stop video preview")
        
    def hideStarView(self):
        """
        Hides the star view preview
        """
        err = OpticstarDLL.show_star_view(False)
        if err != 0:
            raise Exception("Could not hide Star View")     

    def isExposing(self):
        isExposing = c_bool()
        timeLeft = c_uint()
        err = OpticstarDLL.is_exposing(byref(isExposing), byref(timeLeft))
        if err != 0: Exception("Could not get if exposing")
        if self.logging: print("Exposing result is: %s %s" % (str(isExposing), str(timeLeft)))
        return isExposing.value
    
    def getFrame(self, exposureTime):
        """
        Captures an image in binning mode 0 with the specified exposure time
        """
        if self.logging: print("Capturing image with exposure time %d ms" % exposureTime)
        err = OpticstarDLL.capture(0, exposureTime)
        if (err != 0):
            raise Exception("Could not capture image")
        else:
            if self.logging: print("Capture returned successfully. Getting raw image.")
            width = 1360
            height = 1024
            array = bytearray(width * height * 2)
            err2 = OpticstarDLL.get_raw_image(0, 0, width, height, array)
            if (err2 != 0):
                raise Exception("Could not get the raw image")
            else:
                if self.logging: print("Raw image returned successfully.")
                return array
        return None
            
