import numpy as np
import scipy.io
import cv2
import time
from ctypes import *
from pyicic.IC_ImagingControl import IC_ImagingControl

class LifetimeImager:

	def __init__(self, frames=100, preview=False, filename=""):
		self.frames = 100
		self.filename = ""
		return self
		
	def setFrames(self, frames):
		self.frames = frames
		return self
		
	def setOutputFilename(self, filename):
		self.filename = filename
	
	def getFilename(self):
		if (self.filename == ""):
			self.filename = "output_%s_%d" % (self.timestamp, frames)
		return self.filename
	def initCamera(self):
		self.icic = IC_ImagingControl()
		self.icic.init_library()
		cam_names = self.icic.get_unique_device_names()
		self.camName = cam_names[0]
		self.cam = self.icic.get_device(self.camName)
		self.cam.open()
		self.cam.set_video_norm('PAL_B')
		self.imgHeight = self.cam.get_video_format_height()
		self.imgWidth = self.cam.get_video_format_width()
		self.imgDepth = 3 # 3 colours for RGB
		self.bufferSize = self.imgHeight * self.imgWidth * self.imgDepth * sizeof(c_uint8)
		self.timestamp = time.strftime("_%Y%m%d_%H%M%S")
		self.cam.enable_trigger(True)
		if not self.cam.callback_registered:
			self.cam.register_frame_ready_callback()
		self.cam.enable_continuous_mode(True)
		print("Camera %s initialised. Resolution is %d x $d" % (self.camName, self.imgWidth, self.imgHeight))
		
	def captureFrame(self):
		self.cam.reset_frame_ready();
		self.cam.wait_til_frame_ready(3000);

		img_ptr = self.cam.get_buffer()
		img_data = cast(img_ptr, POINTER(c_ubyte * self.buffer_size))

		return np.ndarray(buffer = img_data.contents, dtype = np.uint8, shape = (self.img_height, self.img_width, self.img_depth))
		
	def preview(self):
		self.initCamera()
		self.cam.start_live(show_display=False) # start imaging
		i = 0
		total = None
		while(True):
			i++
			if (i % self.frames == 0):
				total = None
			frame = captureFrame()
			if (total == None):
				total = np.ndarray([len(temp_img), len(temp_img[0]), 3], "uint32")
			total = np.add(temp_img, total);
			img = np.divide(total,i).astype("uint8");
			cv2.imshow('Image', img) 
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
		self.cam.stop_live()
		self.icic.close_library()
		cv2.destroyAllWindows()
		
	def saveOutput(self, total, img, now):
		self.elapsed = time.time() - now
		print("Capture finished in %0.2f seconds" % (self.elapsed))
		cv2.imwrite(self.filename + ".png", img)
		image = np.mean(total, axis=2)
		scipy.io.savemat(self.fileOutput + ".dat", mdict={'image': image})
		textFile = open(self.fileOutput + ".par", "w")
		textFile.write("Frames: %d\n" % self.frames)
		textFile.write("Date: %s\n" % self.timestamp)
		textFile.write("Time Taken : %0.2fs\n" % self.elapsed)
		textFile.write("Width: %d\n" % self.img_width)
		textFile.write("Height: %d\n" % self.img_height)
		textFile.close()
		print("Output saved to %s" % (self.fileOutput))
		
	def capture(self):
		try:
			self.initCamera()
			self.cam.start_live(show_display=False) # start imaging
			i = 0
			total = None
			now = time.time()
			while(i < self.frames):
				i++
				frame = captureFrame()
				if (total == None):
					total = np.ndarray([len(temp_img), len(temp_img[0]), 3], "uint32")
				total = np.add(temp_img, total);
				img = np.divide(total,i).astype("uint8");
				cv2.imshow('Image', img) 
				if cv2.waitKey(1) & 0xFF == ord('q'):
					break
				if (self.frames == i):
					saveOutput(total, img, now)
				
			self.cam.stop_live()
			self.icic.close_library()
			cv2.destroyAllWindows()
			return True
		except Exception:
			return False
