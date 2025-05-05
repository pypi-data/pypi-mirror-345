#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Version 0.7.16+ required.

import os
import sys
import spplugin


def audiorwexample(ifilename, ofilename):
    data, samprate, params = spplugin.audioread(ifilename)
    print('nread = %d' % len(data))
    print('samprate = ' + str(samprate) + ', params =\n' + str(params))

    if False:
        nwframes = spplugin.audiowrite(ofilename, data, samprate,
                                       sampbit=params['sampbit'])
    else:
        nwframes = spplugin.audiowrite(ofilename, data, params=params)
    print('write frames = %d' % nwframes)

    data2, samprate2, params2 = spplugin.audioread(ofilename)
    print('reload: nread = %d' % len(data2))
    print('reload: samprate = ' + str(samprate2) + ', params =\n' + str(params2))


if __name__ == '__main__':
    if len(sys.argv) <= 2:
        print('usage: %s ifilename ofilename'
              % os.path.basename(sys.argv[0]), file=sys.stderr)
        quit()

    audiorwexample(sys.argv[1], sys.argv[2])
