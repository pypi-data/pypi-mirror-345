#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import spaudio

a = spaudio.SpAudio()

a.setnchannels(1)
a.setsamprate(8000)

a.open('ro')

y = a.createndarray(16000)

nread = a.read(y)
print('nread = %d' % nread)

a.close()

a.open('wo')

nwrite = a.write(y)
print('nwrite = %d' % nwrite)

a.close()

x = np.linspace(0.0, 2.0, 16000)
plt.plot(x, y)
plt.xlim(0.0, 2.0)
plt.xlabel('Time [s]')
plt.ylabel('Amplitude (normalized)')
plt.show()
