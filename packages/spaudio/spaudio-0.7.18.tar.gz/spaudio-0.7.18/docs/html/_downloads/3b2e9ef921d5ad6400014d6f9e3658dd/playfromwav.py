#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import wave
import spaudio


def playfromwav(filename):
    with wave.open(filename, 'rb') as wf:
        nchannels = wf.getnchannels()
        samprate = wf.getframerate()
        sampwidth = wf.getsampwidth()
        nframes = wf.getnframes()
        print('nchannels = %d, samprate = %d, sampwidth = %d, nframes = %d'
              % (nchannels, samprate, sampwidth, nframes))

        a = spaudio.SpAudio()

        a.setnchannels(nchannels)
        a.setsamprate(samprate)
        a.setsampwidth(sampwidth)

        b = wf.readframes(nframes)

        a.open('wo')

        nwrite = a.writeraw(b)
        print('nwrite = %d' % nwrite)

        a.close()


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('usage: %s filename'
              % os.path.basename(sys.argv[0]), file=sys.stderr)
        quit()

    playfromwav(sys.argv[1])
