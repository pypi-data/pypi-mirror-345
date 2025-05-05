#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Version 0.7.15+ required.

import argparse
import spplugin
import spaudio


def playrawbyplugin(filename, samprate, nchannels, sampbit, filetype):
    with spplugin.open(filename, 'r', pluginname='input_raw', samprate=samprate,
                       nchannels=nchannels, sampbit=sampbit, filetype=filetype) as pf:
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
            b = pf.readframes(nframes)
            print('nread = %d' % len(b))

            nwframes = a.writeframes(b)
            print('write frames = %d' % nwframes)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Play an audio file including a raw file')
    parser.add_argument('filename', help='name of input file')
    parser.add_argument('-f', '--samprate', type=int,
                        default=8000, help='sampling rate [Hz]')
    parser.add_argument('-c', '--nchannels', type=int,
                        default=1, help='number of channels')
    parser.add_argument('-b', '--sampbit', type=int,
                        default=16, help='bits/sample')
    parser.add_argument('-t', '--filetype', help='file type string')
    args = parser.parse_args()

    playrawbyplugin(args.filename, args.samprate, args.nchannels,
                    args.sampbit, args.filetype)
