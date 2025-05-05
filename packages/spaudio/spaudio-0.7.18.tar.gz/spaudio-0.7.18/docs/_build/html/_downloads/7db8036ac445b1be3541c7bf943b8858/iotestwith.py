#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Version 0.7.15+ required.

import spaudio

with spaudio.open('rw', nchannels=2, samprate=44100, buffersize=2048) as a:
    nloop = 500
    b = bytearray(4096)

    for i in range(nloop):
        a.readraw(b)
        a.writeraw(b)
