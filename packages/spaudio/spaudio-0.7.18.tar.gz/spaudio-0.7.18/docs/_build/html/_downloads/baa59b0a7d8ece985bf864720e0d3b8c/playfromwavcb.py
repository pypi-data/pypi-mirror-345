#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import wave
import spaudio


def myaudiocb(audio, cbtype, cbdata, args):
    if cbtype == spaudio.OUTPUT_POSITION_CALLBACK:
        position = cbdata
        samprate = args[0]
        nframes = args[1]
        position_s = float(position) / float(samprate)
        total_s = float(nframes) / float(samprate)
        sys.stdout.write('Time: %.3f / %.3f\r' % (position_s, total_s))
    elif cbtype == spaudio.OUTPUT_BUFFER_CALLBACK:
        buf = cbdata
        # print('OUTPUT_BUFFER_CALLBACK: buffer type = %s, size = %d' % (type(buf), len(buf)))
    return True


def playfromwav(filename):
    with wave.open(filename, 'rb') as wf:
        nchannels = wf.getnchannels()
        samprate = wf.getframerate()
        sampwidth = wf.getsampwidth()
        nframes = wf.getnframes()
        print('nchannels = %d, samprate = %d, sampwidth = %d, nframes = %d'
              % (nchannels, samprate, sampwidth, nframes))

        a = spaudio.SpAudio()

        a.setbuffersize(1024)
        a.setnchannels(nchannels)
        a.setsamprate(samprate)
        a.setsampwidth(sampwidth)

        b = wf.readframes(nframes)

        a.setcallback(spaudio.OUTPUT_POSITION_CALLBACK | spaudio.OUTPUT_BUFFER_CALLBACK,
                      myaudiocb, samprate, nframes)

        a.open('wo')

        nwrite = a.writeraw(b)
        # print('nwrite = %d' % nwrite)

        a.close()


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('usage: %s filename'
              % os.path.basename(sys.argv[0]), file=sys.stderr)
        quit()

    playfromwav(sys.argv[1])
