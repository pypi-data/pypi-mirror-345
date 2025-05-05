#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Version 0.7.16+ required.

import spaudio

blocklen = 8192
nchannels = 2
samprate = 44100
nframes = 88200  # 2.0 [s]

a = spaudio.SpAudio()

a.open('ro', nchannels=nchannels, samprate=samprate)

b = a.readframes(nframes, arraytype='array')
print('nread = %d' % len(b))

a.close()

a.open('wo', nchannels=nchannels, samprate=samprate)

nwframes = a.writeframes(b)
print('write frames = %d' % nwframes)

a.close()
