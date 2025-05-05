#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Version 0.7.15+ required.

import os
import sys
import spplugin
import spaudio


def playfilebyplugin(filename):
    with spplugin.open(filename, 'r') as pf:
        print('input plugin: %s (%s)' % (pf.getpluginid(), pf.getplugindesc()))
        print('plugin version: %d.%d' % pf.getpluginversion())

        nchannels = pf.getnchannels()
        samprate = pf.getsamprate()
        sampbit = pf.getsampbit()
        nframes = pf.getnframes()
        print('nchannels = %d, samprate = %d, sampbit = %d, nframes = %d'
              % (nchannels, samprate, sampbit, nframes))

        filetype = pf.getfiletype()
        filedesc = pf.getfiledesc()
        filefilter = pf.getfilefilter()
        if filetype:
            print('filetype = %s %s'
                  % (filetype, '(' + filedesc +
                     ('; ' + filefilter if filefilter else '') + ')' if filedesc else ''))
        songinfo = pf.getsonginfo()
        if songinfo:
            print('songinfo = ' + str(songinfo))

        with spaudio.open('wo', nchannels=nchannels, samprate=samprate,
                          sampbit=sampbit) as a:
            b = a.createarray(nframes, True)
            nread = pf.read(b)
            print('nread = %d' % nread)

            nwrite = a.write(b)
            print('nwrite = %d' % nwrite)


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('usage: %s filename'
              % os.path.basename(sys.argv[0]), file=sys.stderr)
        quit()

    playfilebyplugin(sys.argv[1])
