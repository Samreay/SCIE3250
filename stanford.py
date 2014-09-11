#!/bin/env python

# Copyright (c) 2008 Daniel Gruber <daniel@tydirium.org>

# Permission to use, copy, modify, and distribute this software for
# any purpose with or without fee is hereby granted, provided that the
# above copyright notice and this permission notice appear in all
# copies.

# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
# WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
# AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL
# DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA
# OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

import instrument

class StanfordPicos4(instrument.Instrument):
    '''Stanford Research Picos 4 ICCD'''

    def __init__(self,address='COM1'):
        instrument.Instrument.__init__(\
            self,'serial',address,'Stanford Research Picos 4 ICCD')

        # device specific serial settings
        self.handle.setBaudrate(9600)
        self.handle.setRtsCts(1)
        self.handle.setParity('N')
        self.handle.setByteSize(8)
        self.handle.setStopbits(1)
        self.handle.setTimeout(0.1)

        # set to gamma = 1
        self.write('y1\r\n')

        # set to frame mode
        self.write('f0\r\n')

        self.__cleanbuffer()

    def __cleanbuffer(self):
        res=self.readline() 
        while res != '':
            res=self.readline()

    def __str__(self):
        str = "Stanford Picos 4 ICCD (texp = %e s, " % self.GetExposureTime()\
            + "tdel = %e s, " % self.GetExposureDelay()\
            + "MCP %i V, " % self.GetGain()\
            + "trigger is %s)" % self.GetTriggerSource()

        return str

    def reset(self):
        self.write('i\r\n')
        self.__cleanbuffer()

    def SetGain(self,gain):
        '''Set MCP gain (in V)'''
        if gain >= 0 and gain <=1000:
            self.write('g%i\r\n' % int(gain))
            self.__cleanbuffer()
        else:
            raise ValueError,'MCP gain must be between 0 and 1000V!'

    def GetGain(self):
        '''Get MCP gain in V'''
        self.write('s\r\n')
        res='x'
        gain='unknown'
        while res is not '':
            res=self.readline()
            if res[0:5] == 'Gain=':
                gain=int(float(res[5:].rstrip('V\r\n')))

        self.__cleanbuffer()
        return gain

    def SetExposureTime(self,exptime):
        '''Set exposure time in s'''
        self.write('t%e\r\n' % exptime)
        self.__cleanbuffer()

    def GetExposureTime(self):
        '''Get exposure time in s'''
        self.write('s\r\n')
        res='x'
        exptime='unknown'
        while res is not '':
            res=self.readline()
            if res[0:7] == 'Time = ':
                exptime=float(res[7:res.find('s')])

        self.__cleanbuffer()
        return exptime

    def SetExposureDelay(self,delay):
        '''Set delay after trigger in s'''
        self.write('d%e\r\n' % delay)
        self.__cleanbuffer()

    def GetExposureDelay(self):
        '''Get delay after trigger in s'''
        self.write('s\r\n')
        res='x'
        delay='unknown'
        while res is not '':
            res=self.readline()
            if res[0:7] == 'Time = ':
                # XXX ugly hack
                delay=float(res[res.find('y')+3:res.find('s',20)])

        self.__cleanbuffer()
        return delay

    def SetTriggerSource(self,trigger='Fsync'):
        '''Set trigger source (either 'FSync' or 'external')''' 
        if trigger == 'Fsync':
            self.write('cf\r\n')
        elif trigger == 'external':
            self.write('c-\r\n')
        else:
            raise ValueError,'Trigger source must be either Fsync or external!'

        self.__cleanbuffer()

    def GetTriggerSource(self):
        '''Get trigger source (either 'FSync' or "external')'''
        self.write('s\r\n')
        res='x'
        trigger='unknown'
        while res is not '':
            res=self.readline()
            if res == 'Fsync out  connected to -Trig in\r\n':
                return 'FSync'
            elif res == 'externally triggered, use -Trig/+Trig\r\n':
                return 'external'

        self.__cleanbuffer()
        return trigger

    def SetVideoGain(self,gain):
        '''Set CCD video gain in db (0 <= gain <= 20)'''

        if gain < 0 or gain > 25:
            raise ValueError,'Video Gain has to be between 0 and 25 dB!'

        self.write('a0\r\n')
        self.__cleanbuffer()        
        self.write('v%i\r\n' % gain)
        self.__cleanbuffer()

    def GetVideoGain(self):
        '''Get CCD video gain in db'''
        self.write('s\r\n')
        res='x'
        vgain='unknown'
        while res is not '':
            res=self.readline()
            if res[0:13] == 'Video Gain = ':
                # XXX ugly hack
                vgain=int(res[13:15])

        self.__cleanbuffer()
        return vgain

if __name__ == '__main__':
    c=StanfordPicos4()
    print 'Exposure time is %e s' % c.GetExposureTime()
    print 'Delay time is %e s' % c.GetExposureDelay()
    print 'Gain is %i V' % c.GetGain()
    print 'Trigger is %s' % c.GetTriggerSource()
    print 'Video Gain is %i dB' % c.GetVideoGain()
