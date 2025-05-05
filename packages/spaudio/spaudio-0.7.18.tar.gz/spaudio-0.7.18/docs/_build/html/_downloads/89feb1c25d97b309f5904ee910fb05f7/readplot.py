#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import spaudio
import matplotlib.pyplot as plt

a = spaudio.SpAudio()

a.setnchannels(1)
a.setsamprate(8000)

a.open('ro')

b = a.createarray(16000)

nread = a.read(b)
print('nread = %d' % nread)

a.close()

a.open('wo')

nwrite = a.write(b)
print('nwrite = %d' % nwrite)

a.close()

plt.plot(b)
plt.show()
