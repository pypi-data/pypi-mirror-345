#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Version 0.7.15+ required.

import os
import sys
import wave
import spaudio


def playfromwav2(filename):
    with wave.open(filename, 'rb') as wf:
        paramstuple = wf.getparams()
        print('nchannels = %d, framerate = %d, sampwidth = %d, nframes = %d'
              % (paramstuple.nchannels, paramstuple.framerate,
                 paramstuple.sampwidth, paramstuple.nframes))

        with spaudio.open('wo', params=paramstuple) as a:
            b = wf.readframes(paramstuple.nframes)
            nwrite = a.writeraw(b)
            print('nwrite = %d' % nwrite)


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('usage: %s filename'
              % os.path.basename(sys.argv[0]), file=sys.stderr)
        quit()

    playfromwav2(sys.argv[1])
