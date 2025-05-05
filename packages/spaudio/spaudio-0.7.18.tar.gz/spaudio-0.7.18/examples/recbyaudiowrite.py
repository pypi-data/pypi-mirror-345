#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Version 0.7.16+ required.

import argparse
import spplugin
import spaudio


def recbyaudiowrite(filename, samprate, nchannels, sampbit,
                    filetype, duration):
    with spaudio.open('ro', samprate=samprate, nchannels=nchannels, 
                      sampbit=sampbit) as a:
        nframes = round(duration * samprate)
        data = a.readframes(nframes, channelwise=True)
        print('nread = %d' % len(data))

        nwframes = spplugin.audiowrite(filename, data, samprate, sampbit=sampbit,
                                       pluginname='output_raw', filetype=filetype)
        print('write frames = %d' % nwframes)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Record to an audio file by using a plugin')
    parser.add_argument('filename', help='name of output file')
    parser.add_argument('-f', '--samprate', type=int,
                        default=44100, help='sampling rate [Hz]')
    parser.add_argument('-c', '--nchannels', type=int,
                        default=2, help='number of channels')
    parser.add_argument('-b', '--sampbit', type=int,
                        default=16, help='bits/sample')
    parser.add_argument('-t', '--filetype', help='file type string')
    parser.add_argument('-d', '--duration', type=float,
                        default=2.0, help='recording duration [s]')
    args = parser.parse_args()

    recbyaudiowrite(args.filename, args.samprate, args.nchannels,
                    args.sampbit, args.filetype, args.duration)
