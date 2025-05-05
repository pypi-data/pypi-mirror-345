#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import spaudio

a = spaudio.SpAudio()

a.setnchannels(2)
a.setsamprate(44100)
a.setbuffersize(2048)

nloop = 500
b = bytearray(4096)

a.open('r')
a.open('w')

for i in range(nloop):
    a.readraw(b)
    a.writeraw(b)

a.close()
