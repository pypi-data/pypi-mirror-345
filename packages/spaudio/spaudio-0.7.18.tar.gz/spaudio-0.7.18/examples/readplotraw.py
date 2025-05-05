#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import spaudio
import matplotlib.pyplot as plt

a = spaudio.SpAudio()

a.setnchannels(1)
a.setsamprate(8000)

a.open('ro')

b = a.createrawarray(16000)

nread = a.readraw(b)
print('nread = %d' % nread)

a.close()

a.open('wo')

nwrite = a.writeraw(b)
print('nwrite = %d' % nwrite)

a.close()

plt.plot(b)
plt.show()
