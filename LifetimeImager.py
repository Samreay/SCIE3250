import numpy as np
import matplotlib as mpl
import cv2
import time
from ctypes import *
from pyicic.IC_ImagingControl import IC_ImagingControl

print("To use this file, initialise a new object of type LifetimeImager"
      + " (frames \nas optional parameter, default is 250) and then call the capture() method")
print("Output image average and data count data will be found in the folder\n"
      + "in which the python resides")
print("Please note that the camera stream is captured on initilization, \n"
      + "so this program will not work when IC Capture is open and streaming, \n"
      + "or vice versa")
print("\nAs an example, run the following:\n\t LifetimeImager().capture()\n")

class LifetimeImager:

    def __init__(self, frames=250):
        self.frames = frames
        self.fileOutput = "output_%s_%d" % (time.strftime("_%Y%m%d_%H%M%S"), frames)
        self.icic = IC_ImagingControl()
        self.icic.init_library()

        cam_names = self.icic.get_unique_device_names()
        self.cam_name = cam_names[0]
        self.cam = self.icic.get_device(self.cam_name)
        self.cam.open()
        self.cam.set_video_norm('PAL_B')

        self.img_height = self.cam.get_video_format_height()
        self.img_width = self.cam.get_video_format_width()
        self.img_depth = 3     # 3 colours for RGB
        self.buffer_size = self.img_height * self.img_width * self.img_depth * sizeof(c_uint8)

        print("LifetimeImager initialised for %d frames, outputting to %s from source %s" % (self.frames, self.fileOutput, self.cam_name))
    
    def capture(self):
        
        self.cam.enable_trigger(True)
        if not self.cam.callback_registered:
            self.cam.register_frame_ready_callback()
            self.cam.enable_continuous_mode(True)
        self.cam.start_live(show_display=False)
                
        total = None;
        i = 0
        print("Capturing frames now")
        now = time.time();
        while(i < self.frames):
            i = i + 1

            self.cam.reset_frame_ready();
            self.cam.wait_til_frame_ready(3000);



            img_ptr = self.cam.get_buffer()
            img_data = cast(img_ptr, POINTER(c_ubyte * self.buffer_size))

            temp_img = np.ndarray(buffer = img_data.contents,
                                  dtype = np.uint8,
                                  shape = (self.img_height, self.img_width, self.img_depth))
            if (total == None):
                total = np.ndarray([len(temp_img), len(temp_img[0]), 3], "uint32")
            total = np.add(temp_img, total);
            img = np.divide(total,i).astype("uint8");
            cv2.imshow('Image', img) 

            # Display the resulting frame
            if (i == self.frames):
                cv2.imwrite(self.fileOutput + ".png", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # When everything done, release the capture
        print("Capture finished in %0.2f seconds" % (time.time() - now))
        self.cam.stop_live()
        self.icic.close_library()
        
        cv2.destroyAllWindows()
        if (total != None):
            np.savetxt(self.fileOutput + ".dat", np.mean(total, axis=2), "%d", ",")
            print("Output saved to %s" % (self.fileOutput))

