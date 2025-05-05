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

nread = a.read(b)
print('nread = %d' % nread)

a.close()

a.open('wo', nchannels=nchannels, samprate=samprate)
nloop = ((nframes * nchannels) + blocklen - 1) // blocklen  # ceil

for i in range(nloop):
    nwrite = a.write(b, offset=(i * blocklen), length=blocklen)
    print('%d: write = %d' % (i, nwrite))

a.close()
