#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Version 0.7.16+ required.

import os
import sys
import spplugin
import spaudio


def audioreadexample(filename):
    data, samprate, params = spplugin.audioread(filename)
    print('samprate = ' + str(samprate) + ', params =\n' + str(params))

    with spaudio.open('wo', params=params) as a:
        nwframes = a.writeframes(data)
        print('write frames = %d' % nwframes)


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('usage: %s filename'
              % os.path.basename(sys.argv[0]), file=sys.stderr)
        quit()

    audioreadexample(sys.argv[1])
