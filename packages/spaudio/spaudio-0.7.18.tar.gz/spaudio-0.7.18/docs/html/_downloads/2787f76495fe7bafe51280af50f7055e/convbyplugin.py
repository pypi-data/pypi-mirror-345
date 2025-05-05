#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import spplugin


def convbyplugin(inputfile, outputfile):
    with spplugin.open(inputfile, 'r') as pf:
        print('input plugin: %s (%s)' % (pf.getpluginid(), pf.getplugindesc()))
        print('plugin version: %d.%d' % pf.getpluginversion())

        params = pf.getparams()
        print('nchannels = %d, samprate = %d, sampbit = %d, nframes = %d'
              % (params['nchannels'], params['samprate'], params['sampbit'],
                 params['nframes']))

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

        with spplugin.open(outputfile, 'w', params=params) as pf:
            print('output plugin: %s (%s)' % (pf.getpluginid(), pf.getplugindesc()))
            print('plugin version: %d.%d' % pf.getpluginversion())

            nwrite = pf.writeraw(b)
            print('nwrite = %d' % nwrite)

            print('output file: %s' % outputfile, file=sys.stderr)


if __name__ == '__main__':
    if len(sys.argv) <= 2:
        print('usage: %s inputfile outputfile'
              % os.path.basename(sys.argv[0]), file=sys.stderr)
        quit()

    convbyplugin(sys.argv[1], sys.argv[2])
