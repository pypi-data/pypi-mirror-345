#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import aifc
import wave
import sunau
import spplugin


def writefrombyplugin(inputfile, outputfile):
    _, ifileext = os.path.splitext(inputfile)
    if ifileext in ('.wav', '.wave'):
        sndlib = wave
        decodebytes = True
        ibigendian_or_signed8bit = False
    elif ifileext == '.au':
        sndlib = sunau
        decodebytes = True
        ibigendian_or_signed8bit = True
    elif ifileext in ('.aif', '.aiff', '.aifc', '.afc'):
        sndlib = aifc
        decodebytes = False
        ibigendian_or_signed8bit = True
    else:
        raise RuntimeError('input file format is not supported')

    with sndlib.open(inputfile, 'rb') as sf:
        params = sf.getparams()

        print('nchannels = %d, framerate = %d, sampwidth = %d, nframes = %d'
              % (params.nchannels, params.framerate, params.sampwidth, params.nframes))

        if params.comptype:
            print('comptype = %s %s'
                  % (params.comptype, '(' + params.compname +
                     ')' if params.compname else ''))

        y = sf.readframes(params.nframes)

        with spplugin.open(outputfile, 'w', params=params) as pf:
            print('output plugin: %s (%s)' % (pf.getpluginid(), pf.getplugindesc()))
            print('plugin version: %d.%d' % pf.getpluginversion())

            b = pf.copyraw2array(y, params.sampwidth, bigendian_or_signed8bit=ibigendian_or_signed8bit)
            nwrite = pf.writeraw(b)
            print('nwrite = %d' % nwrite)

            print('output file: %s' % outputfile, file=sys.stderr)


if __name__ == '__main__':
    if len(sys.argv) <= 2:
        print('usage: %s inputfile outputfile'
              % os.path.basename(sys.argv[0]), file=sys.stderr)
        quit()

    writefrombyplugin(sys.argv[1], sys.argv[2])
