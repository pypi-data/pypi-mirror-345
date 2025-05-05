#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Version 0.7.15+ required.

import spaudio

blocklen = 8192
nchannels = 2
samprate = 44100
nframes = 88200  # 2.0 [s]

a = spaudio.SpAudio()

a.open('ro', nchannels=nchannels, samprate=samprate)
b = a.createarray(nframes, True)
nloop = ((nframes * nchannels) + blocklen - 1) // blocklen  # ceil

for i in range(nloop):
    nread = a.read(b, offset=(i * blocklen), length=blocklen)
    print('%d: nread = %d' % (i, nread))

a.close()

a.open('wo', nchannels=nchannels, samprate=samprate)

nwrite = a.write(b)
print('nwrite = %d' % nwrite)

a.close()
