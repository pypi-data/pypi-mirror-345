#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Version 0.7.16+ required.

import numpy as np
import matplotlib.pyplot as plt
import spaudio

with spaudio.open('ro', nchannels=2, samprate=44100) as a:
    y = a.readframes(44100, channelwise=True)
    print('nread = %d' % len(y))

    x = np.linspace(0.0, 1.0, 44100)
    for i in range(a.getnchannels()):
        plt.plot(x, y[:, i])
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude (normalized)')
    plt.show()
