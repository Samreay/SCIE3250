#!/bin/env python

# Copyright (c) 2007, 2008 Daniel Gruber <daniel@tydirium.org>

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

import serial

class Instrument:
    '''Abstract base class for a laboratory instrument'''

    def __init__(self,instrtype,address,name="Generic instrument"):
        self.name=name
        self.address=address
        self.instrtype=instrtype
        self.debug=False

        if self.instrtype is 'serial':
            self.handle=serial.Serial(self.address,timeout=10)
        else:
            raise ValueError,'Instrument type unknown!'
        
    def write(self,str):
        if self.debug:
            print(str)
        self.handle.write(str)
    
    def read(self,len=512):
        res=self.handle.read(len)

        if res == '':
            raise ValueError,'No answer from instrument!'
        
        if self.debug:
            print(res)
        return res

    def readline(self):
        res=self.handle.readline()
        if self.debug:
            print(res)
        return res

    def close(self):
        self.handle.close()

    def query(self,text,len=512):
        self.write(text)
        return self.readline()

    def __str__(self):
        return "%s at %s %s" % (self.name,self.type,self.address)

    def __del__(self):
        self.close()
        


