#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Version 0.7.16+ required.

import os
import sys
import spplugin
import spaudio


def audiowriteexample(filename):
    duration = 2.0
    with spaudio.open('ro', nchannels=2, samprate=44100) as a:
        nframes = round(duration * a.getsamprate())
        data = a.readframes(nframes, channelwise=True)
        print('nread = %d' % len(data))

        nwframes = spplugin.audiowrite(filename, data, a.getsamprate())
        print('write frames = %d' % nwframes)


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('usage: %s filename'
              % os.path.basename(sys.argv[0]), file=sys.stderr)
        quit()

    audiowriteexample(sys.argv[1])
