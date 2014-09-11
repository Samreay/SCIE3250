import numpy as np
import cv2
import time
from ctypes import *
from pyicic.IC_ImagingControl import IC_ImagingControl

class LifetimeImager:

    def __init__(self, frames=100, preview=False, filename=""):
        self.frames = frames
        self.preview = preview
        self.timestamp = time.strftime("_%Y%m%d_%H%M%S")
        if (filename == ""):
            self.fileOutput = "output_%s_%d" % (self.timestamp, frames)
        else:
            self.fileOutput = filename
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
        try:
            self.cam.enable_trigger(True)
            if not self.cam.callback_registered:
                self.cam.register_frame_ready_callback() # needed to wait for frame ready callback
            self.cam.enable_continuous_mode(True)        # image in continuous mode
            self.cam.start_live(show_display=False)       # start imaging
                            
            total = None;
            i = 0
            print("Capturing frames now")
            now = time.time();
            while(i < self.frames or self.preview):
                i = i + 1
                if (self.preview and i % self.frames == 0):
                    total = None

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

                #rot_img = np.rot90(temp_img, 4)     # rotate image 180 degrees
                cv2.imshow('Image', img) 

                # Display the resulting frame
                """cv2.imshow('frame',img)"""
                if (i == self.frames and self.preview == False):
                    cv2.imwrite(self.fileOutput + ".png", img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # When everything done, release the capture
            self.elapsed = time.time() - now
            print("Capture finished in %0.2f seconds" % (self.elapsed))
            self.cam.stop_live()
            self.icic.close_library()
            
            cv2.destroyAllWindows()
            if (total != None and self.preview == False):
                np.savetxt(self.fileOutput + ".dat", np.mean(total, axis=2), "%d", ",")
                textFile = open(self.fileOutput + ".par", "w")
                textFile.write("Frames: %d\n" % self.frames)
                textFile.write("Date: %s\n" % self.timestamp)
                textFile.write("Time Taken : %0.2fs\n" % self.elapsed)
                textFile.write("Width: %d\n" % self.img_width)
                textFile.write("Height: %d\n" % self.img_height)
                textFile.close()
                print("Output saved to %s" % (self.fileOutput))
            return True
        except Exception:
            return False
                    
