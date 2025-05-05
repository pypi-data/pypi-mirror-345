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


def playfromwav2(filename):
    with wave.open(filename, 'rb') as wf:
        paramstuple = wf.getparams()
        print('nchannels = %d, samprate = %d, sampwidth = %d, nframes = %d'
              % (paramstuple.nchannels, paramstuple.framerate,
                 paramstuple.sampwidth, paramstuple.nframes))

        with spaudio.open('wo', params=paramstuple, buffersize=1024,
                          callback=(spaudio.OUTPUT_POSITION_CALLBACK | spaudio.OUTPUT_BUFFER_CALLBACK,
                                    myaudiocb, paramstuple.framerate, paramstuple.nframes)) as a:
            b = wf.readframes(paramstuple.nframes)
            nwrite = a.writeraw(b)


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('usage: %s filename'
              % os.path.basename(sys.argv[0]), file=sys.stderr)
        quit()

    playfromwav2(sys.argv[1])
