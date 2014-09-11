#!/usr/bin/env python

# Copyright (c) 2008, 2011 Daniel Gruber <daniel@tydirium.org>
# All rights reserved.
#
# Permission to use, copy, modify, and distribute this software for
# any purpose with or without fee is hereby granted, provided that the
# above copyright notice and this permission notice appear in all
# copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
# WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
# AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL
# DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA
# OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

import wx, wx.richtext
import os, time, subprocess, re, threading, sys, traceback
import stanford
from LifetimeImager import LifetimeImager


# begin wxGlade: extracode
# end wxGlade


class LifeTimeFrame(wx.Frame):
    def __init__(self, parent, *args, **kwds):
        # begin wxGlade: LifeTimeFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.panel_3 = wx.Panel(self, -1)
        self.sizer_2_staticbox = wx.StaticBox(self.panel_3, -1, "Messages")
        self.sizer_24_staticbox = wx.StaticBox(self.panel_3, -1, "Measurement Script")
        self.text_ctrl_MeasurementList = wx.TextCtrl(self.panel_3, -1, "", style=wx.TE_MULTILINE)
        self.button_LoadScript = wx.Button(self.panel_3, -1, "Load script")
        self.button_SaveScript = wx.Button(self.panel_3, -1, "Save script")
        self.button_Run = wx.Button(self.panel_3, -1, "Run that thing!")
        self.text_ctrl_Messages = wx.richtext.RichTextCtrl(self.panel_3, -1)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.loadScript, self.button_LoadScript)
        self.Bind(wx.EVT_BUTTON, self.saveScript, self.button_SaveScript)
        self.Bind(wx.EVT_BUTTON, self.startStopMeasurement, self.button_Run)
        # end wxGlade
        self.Bind(wx.EVT_CLOSE, self.onClose)

        # write usage hints, this is a little bit longish ..
        self.text_ctrl_Messages.BeginBold()
        self.text_ctrl_Messages.AppendText('#### USAGE HINTS ####')
        self.text_ctrl_Messages.EndBold()
        self.text_ctrl_Messages.Newline()

        self.text_ctrl_Messages.AppendText('All commands operate from one toplevel directory of the measurement which can be set when running the script. The following commands are implemented:')
        self.text_ctrl_Messages.Newline()

        self.text_ctrl_Messages.BeginSymbolBullet('*',20,30)
        self.text_ctrl_Messages.BeginBold()
        self.text_ctrl_Messages.AppendText('subdir(run1): ')
        self.text_ctrl_Messages.EndBold()
        self.text_ctrl_Messages.AppendText('Save the data in subdirectory \'run1\'of the toplevel directory. The directory will be created.')
        self.text_ctrl_Messages.EndSymbolBullet()
        self.text_ctrl_Messages.Newline()

        self.text_ctrl_Messages.BeginSymbolBullet('*',20,30)
        self.text_ctrl_Messages.BeginBold()
        self.text_ctrl_Messages.AppendText('exptime(1.5): ')
        self.text_ctrl_Messages.EndBold()
        self.text_ctrl_Messages.AppendText('Set the exposure time to 1.5 ns')
        self.text_ctrl_Messages.EndSymbolBullet()
        self.text_ctrl_Messages.Newline()

        self.text_ctrl_Messages.BeginSymbolBullet('*',20,30)
        self.text_ctrl_Messages.BeginBold()
        self.text_ctrl_Messages.AppendText('mcp(1000): ')
        self.text_ctrl_Messages.EndBold()
        self.text_ctrl_Messages.AppendText('Set the MCP voltage to 1000V.')
        self.text_ctrl_Messages.EndSymbolBullet()
        self.text_ctrl_Messages.Newline()

        self.text_ctrl_Messages.BeginSymbolBullet('*',20,30)
        self.text_ctrl_Messages.BeginBold()
        self.text_ctrl_Messages.AppendText('frames(100): ')
        self.text_ctrl_Messages.EndBold()
        self.text_ctrl_Messages.AppendText('Average 100 frames')
        self.text_ctrl_Messages.EndSymbolBullet()
        self.text_ctrl_Messages.Newline()

        self.text_ctrl_Messages.BeginSymbolBullet('*',20,30)
        self.text_ctrl_Messages.BeginBold()
        self.text_ctrl_Messages.AppendText('threshold(10): ')
        self.text_ctrl_Messages.EndBold()
        self.text_ctrl_Messages.AppendText('Set every pixel with a value below or equal the threshold value of 10 to zero')
        self.text_ctrl_Messages.EndSymbolBullet()
        self.text_ctrl_Messages.Newline()

        self.text_ctrl_Messages.BeginSymbolBullet('*',20,30)
        self.text_ctrl_Messages.BeginBold()
        self.text_ctrl_Messages.AppendText('single(10,bg): ')
        self.text_ctrl_Messages.EndBold()
        self.text_ctrl_Messages.AppendText('Take a single image with 10 ns delay, save it in files \'bg.bin\' and \'bg.txt\'')
        self.text_ctrl_Messages.EndSymbolBullet()
        self.text_ctrl_Messages.Newline()

        self.text_ctrl_Messages.BeginSymbolBullet('*',20,30)
        self.text_ctrl_Messages.BeginBold()
        self.text_ctrl_Messages.AppendText('series(65,86,1): ')
        self.text_ctrl_Messages.EndBold()
        self.text_ctrl_Messages.AppendText('Make a series of measurement with delay going from 65 ns to 86 ns in steps of 1 ns.')
        self.text_ctrl_Messages.EndSymbolBullet()
        self.text_ctrl_Messages.Newline()

        self.text_ctrl_Messages.BeginBold()
        self.text_ctrl_Messages.AppendText('#### SCRIPT OUTPUT ####')
        self.text_ctrl_Messages.EndBold()
        self.text_ctrl_Messages.Newline()

        # write default values in measurement list
        self.text_ctrl_MeasurementList.AppendText('# default values\n'+
            'exptime(1.0)\nframes(100)\nmcp(750)\nthreshold(0)\n'+
            '# measurement\nsingle(0,bg)')
        
        self.parent = parent

        self.measurement = threading.Thread(None,self.runScript)
        self.isRunning= False
        self.stopFlag = threading.Event()

    def __set_properties(self):
        # begin wxGlade: LifeTimeFrame.__set_properties
        self.SetTitle("Lifetime Measurements")
        self.text_ctrl_MeasurementList.SetMinSize((250, 300))
        self.text_ctrl_Messages.SetMinSize((250,300))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: LifeTimeFrame.__do_layout
        sizer_17 = wx.BoxSizer(wx.VERTICAL)
        sizer_21 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2 = wx.StaticBoxSizer(self.sizer_2_staticbox, wx.HORIZONTAL)
        sizer_24 = wx.StaticBoxSizer(self.sizer_24_staticbox, wx.HORIZONTAL)
        sizer_35 = wx.BoxSizer(wx.VERTICAL)
        sizer_36_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_35.Add(self.text_ctrl_MeasurementList, 1, wx.ALL|wx.EXPAND, 5)
        sizer_36_copy.Add(self.button_LoadScript, 1, wx.ALL|wx.EXPAND, 5)
        sizer_36_copy.Add(self.button_SaveScript, 1, wx.ALL|wx.EXPAND, 5)
        sizer_35.Add(sizer_36_copy, 0, wx.EXPAND, 0)
        sizer_35.Add(self.button_Run, 0, wx.ALL|wx.EXPAND, 5)
        sizer_24.Add(sizer_35, 1, wx.ALL|wx.EXPAND, 5)
        sizer_21.Add(sizer_24, 0, wx.ALL|wx.EXPAND, 0)
        sizer_2.Add(self.text_ctrl_Messages, 1, wx.ALL|wx.EXPAND, 10)
        sizer_21.Add(sizer_2, 1, wx.ALL|wx.EXPAND, 5)
        self.panel_3.SetSizer(sizer_21)
        sizer_17.Add(self.panel_3, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_17)
        sizer_17.Fit(self)
        self.Layout()
        # end wxGlade

    def loadScript(self, event): # wxGlade: LifeTimeFrame.<event_handler>
        dlg = wx.FileDialog(self, style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST 
                              | wx.FD_CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            filename=dlg.GetPath()
            self.text_ctrl_MeasurementList.Clear()
            self.text_ctrl_MeasurementList.LoadFile(filename)

    def saveScript(self, event): # wxGlade: LifeTimeFrame.<event_handler>
        dlg = wx.FileDialog(self, style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT 
                              | wx.FD_CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            filename=dlg.GetPath()
            self.text_ctrl_MeasurementList.SaveFile(filename)

    def startStopMeasurement(self,event): # wxGlade: LifeTimeFrame.<event_handler>
        if self.isRunning == True:
            # we want to stop the measurement
            self.__info('waiting for measurement to stop ...')
            self.stopFlag.set()
            self.measurement.join()
            self.button_Run.SetLabel('Run measurement!')
            self.isRunning = False
            self.__info('Measurement successfully aborted!')
        else:
            # we want to start the measurement
            self.stopFlag.clear()

            # switch off live preview if it is on
            if self.parent.preview:
                self.parent.preview.poll()
                if self.parent.preview.returncode == None:
                    self.parent.preview.terminate()
                self.parent.preview = None

            try:
                self.measurement.start()
            except:
                # thread was started before and stopped, kill it and start
                self.__debug('caught exception, deleting thread')
                del self.measurement
                self.measurement = threading.Thread(None,self.runScript)
                self.measurement.start()
                
            self.button_Run.SetLabel('Stop measurement!')
            self.isRunning = True
        
    def runScript(self): 
        dlg = wx.DirDialog(self, "Choose data output directory", 
                           defaultPath = os.getcwd(), 
                           style = wx.DD_CHANGE_DIR)
        if dlg.ShowModal() != wx.ID_OK:
            return -1

        del dlg

        # write parameters file
        f=file('parameters.txt','w')

        f.write('# Parameters for lifetime measurement\n')
        f.write('# Start of experiment: %s\n' % time.asctime())
        f.write('# Trigger is %s\n' % self.parent.camera.GetTriggerSource())
        #f.write('# Videogain = %i dB\n' % self.parent.camera.GetVideoGain())

        for linenumber in range(self.text_ctrl_MeasurementList.GetNumberOfLines()):
            text=self.text_ctrl_MeasurementList.GetLineText(linenumber)
            f.write(text+'\n')

        f.close()

        self.exptime=None
        self.threshold=None
        self.frames=None
        self.mcp=None

        self.parent.setupCamera(wx.EVT_BUTTON)

        for linenumber in range(self.text_ctrl_MeasurementList.GetNumberOfLines()):
            text=self.text_ctrl_MeasurementList.GetLineText(linenumber)
            if re.match('^(\w+)\(([\w\,\.\-_]+)\)$',text):
                [command,parameters]=text.rstrip(')').split('(')
                parameters=parameters.split(',')
				# TODO: I THINK THIS IS WHERE I SHOULD ADD THE COMS COMMUNICATION
                res = 0
                if command == 'subdir':
                    res=self.commandSubdir(parameters)
                elif command == 'exptime':
                    self.exptime = float(parameters[0])
                elif command == 'mcp':
                    self.mcp = int(parameters[0])
                elif command == 'frames':
                    self.frames = int(parameters[0])
                elif command == 'threshold':
                    self.threshold = int(parameters[0])
                elif command == 'single':
                    res=self.commandSingle(parameters)
                elif command == 'series':
                    res=self.commandSeries(parameters)
                else:
                    self.__error('%s: unknown command' % command)
                    return -1

                if res != 0:
                    return -1

                if self.stopFlag.isSet():
                    self.__debug('abort flag was set in runScript, aborting ...')
                    return -1

        self.__info('## Script ended %s ## \n' % time.asctime())

        dlg=wx.MessageDialog(self,'Script run finished!','Finished',\
                             wx.OK | wx.ICON_INFORMATION | wx.STAY_ON_TOP)
        dlg.ShowModal()
        self.button_Run.SetLabel('Run measurement')
        self.isRunning = False
        return 0

    def commandSubdir(self,parameters):
        newdir = os.getcwd() + '/' + parameters[0]

        if os.access(newdir,os.X_OK) == False:
            os.mkdir(newdir)

        self.__info('\nchdir to %s\n' % newdir)
        os.chdir(newdir)
        return 0

    def commandSingle(self,parameters):

        if self.frames == None:
            self.__error('Need to set the number of frames to average!')
            return -1

        if self.exptime == None:
            self.__error('Need to set an exposure time!')
            return -1

        if self.mcp == None:
            self.__error('Need to set a MCP voltage!')
            return -1

        if self.threshold == None:
            self.__error('Need to set a pixel threshold!')
            return -1

        delay=float(parameters[0])*1000 # in ps
        filename=parameters[1]
        
        self.__info('\nSingle image with %i frames, ' % self.frames + \
               'exposure time is %i ps, ' % (self.exptime*1000) + \
               'delay time is %i ps, ' % delay + \
               'threshold is %i, ' % self.threshold + \
               'mcp is %i V, ' % self.mcp + \
               'save as %s\n' % filename)

        self.parent.camera.SetExposureDelay(delay*1e-12)
        self.__debug('self.parent.camera.SetExposureDelay(%e)' % (delay*1e-12))
        self.parent.camera.SetExposureTime(self.exptime*1e-9)
        self.__debug('self.parent.camera.SetExposureTime(%e)' % (self.exptime*1e-9))
        self.parent.camera.SetGain(self.mcp)
        self.__debug('self.parent.camera.SetGain(%i)' % (self.mcp))

        self.__info('  imagegrab -n %i ' % self.frames + \
              '-t %i ' % self.threshold + '-o %s\n' % filename)
        ret = LifetimeImager().setFrames(self.frames).setFilename(filename).capture()

        '''ret=subprocess.call([self.parent.exedir + '/imagegrab.exe',\
                         '-n',\
                         '%i' % self.frames, \
                         '-t',\
                         '%i' % self.threshold, \
                         '-o',\
                         '%s' % filename])'''
        if ret != True:
            self.__error('imagegrab.exe returned an error!')
            return -1
        else:
            # append the MCP information to the generated filename.txt
            f=file(filename+'.txt','a')
            f.write("mcp = %f\n" % self.mcp)
            f.write("exptime = %e\n" % (self.exptime*1e-9))
            f.write("delay = %e\n" % (delay * 1e-12))
            f.close()

        return 0

    def commandSeries(self,parameters):

        if self.frames == None:
            self.__error('Need to set the number of frames to average!')
            return -1

        if self.exptime == None:
            self.__error('Need to set an exposure time!')
            return -1

        if self.mcp == None:
            self.__error('Need to set a MCP voltage!')
            return -1

        if self.threshold == None:
            self.__error('Need to set a pixel threshold!')
            return -1

        start=float(parameters[0])*1000
        stop=float(parameters[1])*1000
        step=float(parameters[2])*1000

        self.__info('\nSeries from %i to %i ps, step is %i ps, exp. time is %i ps, \
            %i frames, MCP is %iV, threshold is %i\n'
            % (start,stop,step,self.exptime*1000,self.frames,self.mcp,self.threshold))

        if stop < start:
            self.__error('Startime > Stoptime!')
            return -1

        d = start # in ps
        self.parent.camera.SetExposureTime(self.exptime*1e-9)
        self.__debug('self.parent.camera.SetExposureTime(%e)' % (self.exptime*1e-9))
        self.parent.camera.SetGain(self.mcp)
        self.__debug('self.parent.camera.SetGain(%i)' % (self.mcp))

        while d <= stop:
            if self.stopFlag.isSet():
                self.__debug('abort flag was found in series(), aborting ...')
                return 0
            
            self.parent.camera.SetExposureDelay(d*1e-12)
            self.__debug('self.parent.camera.SetExposureDelay(%e)' % (d*1e-12))

            self.__info('  imagegrab -n %i ' % self.frames +\
                 '-t %i ' % self.threshold + '-o %i' % d + 'ps\n')

            ret=subprocess.call([self. parent.exedir + '/imagegrab.exe',\
                                 '-n',\
                                 '%i' % self.frames,\
                                 '-t',\
                                 '%i' % self.threshold,\
                                 '-o',\
                                 '%i' % int(d) + 'ps'])

            if ret != 0:
                self.__error('imagegrab.exe returned an error!')
                return -1
            else:
                # append the MCP information to the generated filename.txt
                f=file('%i' % int(d) + 'ps','a')
                f.write("mcp = %f\n" % self.mcp)
                f.write("exptime = %e\n" % self.exptime*1e-9)
                f.write("delay = %e\n" % d*1e-12)
                f.close()
                
            d += step

        return 0

    def __error(self,text):
        dlg=wx.MessageDialog(self,text,'Error', wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP)
        dlg.ShowModal()

    def __info(self,text):
        self.__debug(text)
        self.text_ctrl_Messages.AppendText(text)
        self.text_ctrl_Messages.ShowPosition(self.text_ctrl_Messages.GetLastPosition())
        self.Update()

    def __debug(self,text):
        print(text)

    def onClose(self,event):
        self.Hide()
        self.parent.checkbox_TimeResolved.SetValue(False)

# end of class LifeTimeFrame

class MainFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MainFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.panel_1 = wx.Panel(self, -1)
        self.sizer_6_staticbox = wx.StaticBox(self.panel_1, -1, "Live preview")
        self.sizer_3_staticbox = wx.StaticBox(self.panel_1, -1, "Camera settings")
        self.label_9 = wx.StaticText(self.panel_1, -1, "Exposure Time:")
        self.text_ctrl_ExpTime = wx.TextCtrl(self.panel_1, -1, "1")
        self.choice_ExpTime = wx.Choice(self.panel_1, -1, choices=["ns", "us", "ms", "s"])
        self.label_9_copy = wx.StaticText(self.panel_1, -1, "Delay Time:")
        self.text_ctrl_DelayTime = wx.TextCtrl(self.panel_1, -1, "76")
        self.choice_DelayTime = wx.Choice(self.panel_1, -1, choices=["ns", "us", "ms", "s"])
        self.label_8 = wx.StaticText(self.panel_1, -1, "MCP Gain (V):")
        self.text_ctrl_Gain = wx.TextCtrl(self.panel_1, -1, "750")
        self.label_4 = wx.StaticText(self.panel_1, -1, "Trigger:")
        self.choice_TriggerSource = wx.Choice(self.panel_1, -1, choices=["Internal (FSync)", "external"])
        self.label_4_copy = wx.StaticText(self.panel_1, -1, "Video Gain (dB):")
        self.spin_ctrl_VideoGain = wx.SpinCtrl(self.panel_1, -1, "18", min=0, max=20)
        self.checkbox_TimeResolved = wx.CheckBox(self.panel_1, -1, "Time resolved measurement")
        self.button_SetupCamera = wx.Button(self.panel_1, -1, "Setup Camera")
        self.label_1 = wx.StaticText(self.panel_1, -1, "# of frames:")
        self.textCtrlPreviewFrames = wx.TextCtrl(self.panel_1, -1, "25")
        self.buttonPreview = wx.Button(self.panel_1, -1, "Start Live preview")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHECKBOX, self.enableTimeResolved, self.checkbox_TimeResolved)
        self.Bind(wx.EVT_BUTTON, self.setupCamera, self.button_SetupCamera)
        self.Bind(wx.EVT_BUTTON, self.onLivePreview, self.buttonPreview)
        # end wxGlade
        self.Bind(wx.EVT_CLOSE, self.onClose)

        # read the serial port from the registry/config file
        self.conf=wx.Config("LifeTime")

        if(self.conf.HasEntry("Communication/ICCDComPort")):
            port=self.conf.Read("Communication/ICCDComPort")
        else:
            res=self.__getPortFromUser()

            if res == True:
                port=self.conf.Read("Communication/ICCDComPort")
            else:
                self.Destroy()

        try:
            self.camera = stanford.StanfordPicos4('COM1')
        except:
            self.__showError()
            self.Destroy()

        self.ltframe = LifeTimeFrame(self,self)
        self.preview = None
        self.exedir = os.getcwd()

    def __set_properties(self):
        # begin wxGlade: MainFrame.__set_properties
        self.SetTitle("ICCD camera control")
        self.label_9.SetMinSize((80, 12))
        self.choice_ExpTime.SetSelection(0)
        self.label_9_copy.SetMinSize((80, 12))
        self.choice_DelayTime.SetSelection(0)
        self.label_8.SetMinSize((80, 12))
        self.label_4.SetMinSize((80, 12))
        self.choice_TriggerSource.SetSelection(1)
        self.label_4_copy.SetMinSize((80, 12))
        self.label_1.SetMinSize((80, 13))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MainFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_5 = wx.BoxSizer(wx.VERTICAL)
        sizer_6 = wx.StaticBoxSizer(self.sizer_6_staticbox, wx.VERTICAL)
        sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.StaticBoxSizer(self.sizer_3_staticbox, wx.VERTICAL)
        sizer_9 = wx.BoxSizer(wx.VERTICAL)
        sizer_16 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_15 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_11 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_10_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_10 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_10.Add(self.label_9, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_10.Add(self.text_ctrl_ExpTime, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_10.Add(self.choice_ExpTime, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_9.Add(sizer_10, 1, wx.EXPAND, 0)
        sizer_10_copy.Add(self.label_9_copy, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_10_copy.Add(self.text_ctrl_DelayTime, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_10_copy.Add(self.choice_DelayTime, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_9.Add(sizer_10_copy, 1, wx.EXPAND, 0)
        sizer_11.Add(self.label_8, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_11.Add(self.text_ctrl_Gain, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_9.Add(sizer_11, 1, wx.EXPAND, 0)
        sizer_15.Add(self.label_4, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_15.Add(self.choice_TriggerSource, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_9.Add(sizer_15, 1, wx.EXPAND, 0)
        sizer_16.Add(self.label_4_copy, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_16.Add(self.spin_ctrl_VideoGain, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_9.Add(sizer_16, 1, wx.EXPAND, 0)
        sizer_9.Add(self.checkbox_TimeResolved, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_9.Add(self.button_SetupCamera, 0, wx.ALL|wx.EXPAND, 5)
        sizer_3.Add(sizer_9, 1, wx.EXPAND, 5)
        sizer_5.Add(sizer_3, 0, wx.ALL|wx.EXPAND, 5)
        sizer_7.Add(self.label_1, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_7.Add(self.textCtrlPreviewFrames, 1, wx.ALL|wx.EXPAND, 5)
        sizer_6.Add(sizer_7, 1, wx.EXPAND, 0)
        sizer_6.Add(self.buttonPreview, 1, wx.ALL|wx.EXPAND, 5)
        sizer_5.Add(sizer_6, 0, wx.ALL|wx.EXPAND, 5)
        self.panel_1.SetSizer(sizer_5)
        sizer_1.Add(self.panel_1, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        # end wxGlade

    def __getExponent(self,combowidget):
        val=combowidget.GetSelection()

        # all times are in ps!
        if val == 0:
            e=1e3
        elif val == 1:
            e=1e6
        elif val == 2:
            e=1e9
        elif val == 3:
            e=1e12 #Put this because it seems wrong, but check with Taras
        else:
            raise ValueError,'unknown time suffix!'

        return e

    def __error(self,text):
        dlg=wx.MessageDialog(self,text,'Error',\
                                 wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP)
        dlg.ShowModal()

    def setupCamera(self, event): # wxGlade: MainFrame.<event_handler>
        t=int(float(self.text_ctrl_ExpTime.GetValue())*\
              self.__getExponent(self.choice_ExpTime))
        self.camera.SetExposureTime(t*1e-12)

        t=int(float(self.text_ctrl_DelayTime.GetValue())*\
              self.__getExponent(self.choice_DelayTime))
        self.camera.SetExposureDelay(t*1e-12)

        t=int(self.text_ctrl_Gain.GetValue())
        self.camera.SetGain(t)

        t=self.choice_TriggerSource.GetSelection()
        if t == 1:
            self.camera.SetTriggerSource('external')
        else:
            self.camera.SetTriggerSource('Fsync')

        t = self.spin_ctrl_VideoGain.GetValue()
        self.camera.SetVideoGain(t)
        
    def enableTimeResolved(self, event): # wxGlade: MainFrame.<event_handler>
        if self.checkbox_TimeResolved.IsChecked():
            self.ltframe.Show()
            self.ltframe.Raise()
        else:
            self.ltframe.Hide()

    def __getPortFromUser(self):
        if(self.conf.HasEntry("Communication/ICCDComPort")):
            port=self.conf.Read("Communication/ICCDComPort")
        else:
            port = ""
            
        port=wx.GetTextFromUser("COM Port to use?", \
                                "Please enter COM Port for ICCD:",port)
        if port == "":
            wx.MessageBox("No COM port given","No COM port given, aborting ...",\
                          wx.ICON_ERROR | wx.OK)
            return False
        else:
            self.conf.Write("Communication/ICCDComPort",port)
            return True

    def __showError(self):
        message = ''.join(traceback.format_exception(*sys.exc_info()))
        dialog = wx.MessageDialog(None, message, 'Error!', wx.OK|wx.ICON_ERROR)
        dialog.ShowModal()

    def onLivePreview(self, event): # wxGlade: MainFrame.<event_handler>
        numframes=int(self.textCtrlPreviewFrames.GetValue())
        LifetimeImager().setFrames(numframes).preview()

    def onClose(self,event):
        self.Destroy()
        


# end of class MainFrame


if __name__ == "__main__":
    app = wx.App()
	#app = wx.PySimpleApp(0)
    #wx.InitAllImageHandlers()
    frame_1 = MainFrame(None, -1, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
