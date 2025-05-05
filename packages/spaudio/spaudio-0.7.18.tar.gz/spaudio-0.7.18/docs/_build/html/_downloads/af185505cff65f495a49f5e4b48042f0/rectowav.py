#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
import wave
import spaudio


def rectowav(filename, samprate, nchannels, sampwidth, duration):
    with wave.open(filename, 'wb') as wf:
        nframes = round(duration * samprate)
        print('nchannels = %d, samprate = %d, sampwidth = %d, nframes = %d'
              % (nchannels, samprate, sampwidth, nframes))

        a = spaudio.SpAudio()

        a.setnchannels(nchannels)
        a.setsamprate(samprate)
        a.setsampwidth(sampwidth)

        a.open('ro')

        b = a.createrawarray(nframes * nchannels)

        nread = a.readraw(b)
        print('nread = %d' % nread)

        a.close()

        wf.setnchannels(nchannels)
        wf.setframerate(samprate)
        wf.setsampwidth(sampwidth)
        wf.setnframes(nframes)

        wf.writeframes(b)
        print('output file: %s' % filename, file=sys.stderr)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Record to a wave file')
    parser.add_argument('filename', help='name of output wave file')
    parser.add_argument('-f', '--samprate', type=int,
                        default=8000, help='sampling rate [Hz]')
    parser.add_argument('-c', '--nchannels', type=int,
                        default=1, help='number of channels')
    parser.add_argument('-w', '--sampwidth', type=int,
                        default=2, help='sample width [byte]')
    parser.add_argument('-d', '--duration', type=float,
                        default=2.0, help='recording duration [s]')
    args = parser.parse_args()

    rectowav(args.filename, args.samprate, args.nchannels,
             args.sampwidth, args.duration)
