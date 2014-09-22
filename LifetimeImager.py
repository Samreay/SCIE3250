import numpy as np
import scipy.io
import cv2
import time
from ctypes import *
from pyicic.IC_ImagingControl import IC_ImagingControl

class LifetimeImager:

	def __init__(self, frames=100, preview=False, filename=""):
		self.frames = 100
		self.timestamp = time.strftime("_%Y%m%d_%H%M%S")
		self.filename = "output_%s" % (self.timestamp)
		
	def setFrames(self, frames):
		self.frames = frames
		return self
		
	def setFilename(self, filename):
		self.filename = filename
		return self
		
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
		self.cam.enable_trigger(True)
		if not self.cam.callback_registered:
			self.cam.register_frame_ready_callback()
		self.cam.enable_continuous_mode(True)
		print("Camera %s initialised. Resolution is %d x %d" % (self.camName, self.imgWidth, self.imgHeight))
		
	def captureFrame(self):
		self.cam.reset_frame_ready();
		self.cam.wait_til_frame_ready(3000);

		img_ptr = self.cam.get_buffer()
		img_data = cast(img_ptr, POINTER(c_ubyte * self.bufferSize))

		arr = np.ndarray(buffer = img_data.contents, dtype = np.uint8, shape = (self.imgHeight, self.imgWidth, self.imgDepth))
		return np.rot90(arr, 2)
	def preview(self):
		self.initCamera()
		self.cam.start_live(show_display=False) # start imaging
		i = 0
		total = None
		while(True):
			i += 1
			if (i % self.frames == 1):
				i = i % self.frames
				total = None
			frame = self.captureFrame()
			if (total == None):
				total = np.ndarray([len(frame), len(frame[0]), 3], "uint32")
			total = np.add(frame, total);
			img = np.divide(total,i).astype("uint8");
			cv2.imshow('Image', img) 
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
		self.cam.stop_live()
		self.icic.close_library()
		cv2.destroyAllWindows()
		
	def saveOutput(self, total, img, i, now):
		self.elapsed = time.time() - now
		print("Capture finished in %0.2f seconds" % (self.elapsed))
		cv2.imwrite(self.filename + ".png", img)
		image = np.mean(total, axis=2)
		image = (65536 * (image - image.min())/(image.max()-image.min())).astype(np.uint16)
		scipy.io.savemat(self.filename + ".mat", mdict={'image': image})
		textFile = None
		try:
			textFile = open(self.filename + ".par", "w")
			textFile.write("Frames: %d\n" % i)
			textFile.write("Date: %s\n" % self.timestamp)
			textFile.write("Time Taken : %0.2fs\n" % self.elapsed)
			textFile.write("Width: %d\n" % self.imgWidth)
			textFile.write("Height: %d\n" % self.imgHeight)
		finally:
			try:
				textFile.close()
			except Exception:
				print("textFile cannot be closed")
		print("Output saved to %s" % (self.filename))
		
	def capture(self):
		try:
			self.initCamera()
			try:
				print("Camera initialised")
				self.cam.start_live(show_display=False)
				print("Camera started")
				i = 0
				total = None
				now = time.time()
				while(i < self.frames):
					i += 1
					frame = self.captureFrame()
					if (total == None):
						total = np.ndarray([len(frame), len(frame[0]), 3], "uint32")
					total = np.add(frame, total);
					img = np.divide(total,i).astype("uint8");
					cv2.imshow('Image', img) 
					if cv2.waitKey(1) & 0xFF == ord('q'):
						break					
				self.saveOutput(total, img, i, now)
				print("Camera stopped")
				cv2.destroyAllWindows()
			finally:
				self.cam.stop_live()
				self.icic.close_library()
			return True
		except Exception as e:
			print("An error occurred", e.message)
			print("The most likely causes is a background pythonw.exe process using the camera. Kill it.")
			return False
