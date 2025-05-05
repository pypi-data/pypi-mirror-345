#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import aifc
import wave
import sunau
import spplugin


def writefrombyplugin(inputfile, outputfile):
    _, ofileext = os.path.splitext(outputfile)
    if ofileext in ('.wav', '.wave'):
        sndlib = wave
        decodebytes = True
        obigendian_or_signed8bit = False
    elif ofileext == '.au':
        sndlib = sunau
        decodebytes = True
        obigendian_or_signed8bit = True
    elif ofileext in ('.aif', '.aiff', '.aifc', '.afc'):
        sndlib = aifc
        decodebytes = False
        obigendian_or_signed8bit = True
    else:
        raise RuntimeError('output file format is not supported')

    with spplugin.open(inputfile, 'r') as pf:
        print('input plugin: %s (%s)' % (pf.getpluginid(), pf.getplugindesc()))
        print('plugin version: %d.%d' % pf.getpluginversion())

        params = pf.getparams()
        print('nchannels = %d, samprate = %d, sampbit = %d, nframes = %d'
              % (params['nchannels'], params['samprate'], params['sampbit'], params['nframes']))

        if params['filetype']:
            print('filetype = %s %s'
                  % (params['filetype'], '(' + params['filedesc'] +
                     ('; ' + params['filefilter'] if params['filefilter'] else '') +
                     ')' if params['filedesc'] else ''))
        if params['songinfo']:
            print('songinfo = ' + str(params['songinfo']))

        b = pf.createrawarray(params['nframes'], True)
        nread = pf.readraw(b)
        print('nread = %d' % nread)

        paramstuple = pf.getparamstuple(decodebytes)

        with sndlib.open(outputfile, 'wb') as sf:
            sf.setparams(paramstuple)
            y = pf.copyarray2raw(b, paramstuple.sampwidth, bigendian_or_signed8bit=obigendian_or_signed8bit)
            sf.writeframes(y)
            print('output file: %s' % outputfile, file=sys.stderr)


if __name__ == '__main__':
    if len(sys.argv) <= 2:
        print('usage: %s inputfile outputfile'
              % os.path.basename(sys.argv[0]), file=sys.stderr)
        quit()

    writefrombyplugin(sys.argv[1], sys.argv[2])
