# -*- coding: utf-8 -*-
"""
A python module for audio I/O based on `spAudio <https://www-ie.meijo-u.ac.jp/labs/rj001/spLibs/index.html>`_.

Example:
    The following is the example to realize fullduplex audio I/O (version 0.7.15+).
    ::

        import spaudio

        with spaudio.open('rw', nchannels=2, samprate=44100, buffersize=2048) as a:
            nloop = 500
            b = bytearray(4096)

            for i in range(nloop):
                a.readraw(b)
                a.writeraw(b)
"""

import locale
import warnings
import array
from collections import namedtuple
from _spaudio import spaudio_c as _spaudio_c


__version__ = '0.7.18'

OUTPUT_POSITION_CALLBACK = (1 << 0)
OUTPUT_BUFFER_CALLBACK = (1 << 2)

_audio_global = None
_encoding = locale.getpreferredencoding()
_defaultdrivername = _spaudio_c.xspGetAudioDriverName(0)
_ischarbinary = isinstance(_defaultdrivername, bytes)


# https://stackoverflow.com/questions/2166818/how-to-check-if-an-object-is-an-instance-of-a-namedtuple
def _isnamedtupleinstance(x):
    t = type(x)
    b = t.__bases__
    if len(b) != 1 or b[0] != tuple:
        return False
    f = getattr(t, '_fields', None)
    if not isinstance(f, tuple):
        return False
    return all(type(n) == str for n in f)


class Error(Exception):
    """Base exception class for spaudio."""
    pass


class DriverError(Error):
    """Exception raised by audio driver problems."""
    pass


class DeviceError(Error):
    """Exception raised by audio device problems."""
    pass


_StandardLibParams = namedtuple('_standard_lib_params',
                                'nchannels sampwidth framerate nframes comptype compname')
_STANDARD_LIB_KEYS = ['nchannels', 'sampwidth', 'framerate',
                      'nframes', 'comptype', 'compname']

PARAMS_KEYS = ['nchannels', 'sampbit', 'samprate',
               'blockingmode', 'buffersize', 'nbuffers',
               'sampwidth', 'framerate']


def callbacksignature(audio, calltype, cbdata, args):
    """Signature of the callback function for :func:`~spaudio.SpAudio.setcallback` method.

    Args:
        audio (SpAudio): An instance of :class:`~spaudio.SpAudio` class.
        calltype (int): The callback type. ``OUTPUT_POSITION_CALLBACK`` or
            ``OUTPUT_BUFFER_CALLBACK``.
        cbdata: Callback-depend data. A position (int) on ``OUTPUT_POSITION_CALLBACK``
            or a buffer (bytes) on ``OUTPUT_BUFFER_CALLBACK``.
        args: Variable length argument list specified at :func:`~spaudio.SpAudio.setcallback`.
            Note that this `args` variable does not require the prefix ``*``.

    Returns:
        bool: ``False`` if you don't want to fire callbacks anymore.
    """
    return True


class SpAudio:
    """A class for audio I/O.

    Args:
        drivername (str): the driver name to initialize.
    """
    def __init__(self, drivername=None):
        self._audio = None
        self._read_mode = ' '
        self._write_mode = ' '
        self._initdriver(drivername)

    def __del__(self):
        self.terminate()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.terminate()

    def reload(self, drivername=None):
        """Reloads a new audio driver."""
        self.terminate()
        self._initdriver(drivername)

    def terminate(self):
        """Terminates the current audio driver."""
        if self._read_mode[0] == 'r' or self._write_mode[0] == 'w':
            self.close()
        global _audio_global
        if (self._audio is not None) and (self._audio is _audio_global):
            _spaudio_c._spFreeAudioDriver(self._audio)
            _audio_global = None
            self._audio = None

    def _initdriver(self, drivername=None):
        """Initializes the audio driver."""
        if drivername is not None:
            global _ischarbinary
            if _ischarbinary:
                global _encoding
                encodedname = drivername.encode(_encoding)
            else:
                encodedname = drivername
        else:
            encodedname = None
        global _audio_global
        if _audio_global is not None:
            self._audio = _audio_global
        else:
            self._audio = _spaudio_c.spInitAudioDriver(encodedname)
            if self._audio is None:
                raise DriverError('cannot load audio driver')
            _audio_global = self._audio

    def getndevices(self):
        """Gets the number of audio devices."""
        if self._audio is None:
            raise RuntimeError('driver must be loaded')
        flag, numdevice = _spaudio_c.spGetNumAudioDevice(self._audio)
        if flag:
            return numdevice
        else:
            raise DriverError('audio driver error')

    def getdevicename(self, deviceindex):
        """Gets the name of the audio device."""
        if self._audio is None:
            raise RuntimeError('driver must be loaded')
        if deviceindex < 0 or deviceindex >= self.getndevices():
            raise ValueError('0 <= index < %d is required'
                             % self.getndevices())
        name = _spaudio_c.xspGetAudioDeviceName(self._audio, deviceindex)
        if name is not None:
            global _ischarbinary
            if _ischarbinary:
                global _encoding
                return name.decode(_encoding)
            else:
                return name
        else:
            raise DriverError('audio driver error')

    def getdevicelist(self):
        """Gets the list of audio devices."""
        alist = []
        for i in range(self.getndevices()):
            alist.append(self.getdevicename(i))
        return alist

    def selectdevice(self, deviceindex):
        """Selects an audio device which has the index specified.

        Args:
            deviceindex (int): The index associated with an audio device.

        Raises:
            ValueError: If `deviceindex` is greater than or equal to
                the number of devices.
            DriverError: If the audio device cannot be selected.
        """
        if self._audio is None:
            raise RuntimeError('driver must be loaded')
        if deviceindex < 0 or deviceindex >= self.getndevices():
            raise ValueError('0 <= index < %d is required'
                             % self.getndevices())
        flag = _spaudio_c.spSelectAudioDevice(self._audio, deviceindex)
        if not flag:
            raise DriverError('cannot select the audio device')

    def setcallback(self, calltype, func, *args):
        """Sets a callback function.

        Args:
            calltype (int): A combination of callback types.
                ``OUTPUT_POSITION_CALLBACK`` and ``OUTPUT_BUFFER_CALLBACK``
                are supported currently.
            func (callable): Callback function. The callback must have
                a signature in the :func:`~spaudio.callbacksignature` document.
            *args: Variable length argument list.

        Raises:
            DriverError: If the callback function cannot be set.
        """
        if self._audio is None:
            raise RuntimeError('driver must be loaded')
        flag = _spaudio_c.spSetAudioCallbackFunc_(self._audio, calltype,
                                                  (func, self, args))
        if not flag:
            raise DriverError('cannot set a callback function')

    def setsamprate(self, samprate):
        """Sets sample rate of the current device."""
        if self._audio is None:
            raise RuntimeError('driver must be loaded')
        flag = _spaudio_c.spSetAudioSampleRate(self._audio, samprate)
        if not flag:
            raise DriverError('audio driver error')

    def setframerate(self, samprate):
        """Sets sample rate of the current device."""
        self.setsamprate(samprate)

    def getsamprate(self):
        """Gets sample rate of the current device."""
        if self._audio is None:
            raise RuntimeError('driver must be loaded')
        flag, samprate = _spaudio_c.spGetAudioSampleRate(self._audio)
        if flag:
            return samprate
        else:
            raise DriverError('audio driver error')

    def getframerate(self):
        """Gets sample rate of the current device."""
        return self.getsamprate()

    def setsampbit(self, sampbit):
        """Sets bits/sample of the current device. sampbit = 33 means
        32bit float."""
        if self._audio is None:
            raise RuntimeError('driver must be loaded')
        if sampbit < 8:
            raise ValueError('sampbit >= 8 is required')
        flag = _spaudio_c.spSetAudioSampleBit(self._audio, sampbit)
        if not flag:
            raise DriverError('audio driver error')

    def setsampwidth(self, sampwidth, floatflag=False):
        """Sets bytes/sample of the current device."""
        sampbit = sampwidth * 8
        if floatflag:
            sampbit += 1
        return self.setsampbit(sampbit)

    def getsampbit(self):
        """Gets bits/sample of the current device. sampbit = 33 means
        32bit float."""
        if self._audio is None:
            raise RuntimeError('driver must be loaded')
        flag, sampbit = _spaudio_c.spGetAudioSampleBit(self._audio)
        if flag:
            return sampbit
        else:
            raise DriverError('audio driver error')

    def getsampwidth(self):
        """Gets bytes/sample of the current device."""
        return self.getsampbit() // 8

    def getrawsampbit(self):
        """Gets the bits/sample for a raw array."""
        if self._audio is None:
            raise RuntimeError('driver must be loaded')
        flag, sampbit = _spaudio_c.spGetAudioSpecifiedSampleBit(self._audio)
        if flag:
            if sampbit < 16:
                return 16
            elif 16 < sampbit <= 32:
                return 32
            else:
                return sampbit
        else:
            raise DriverError('audio driver error')

    def getrawsampwidth(self):
        """Gets the bytes/sample for a raw array."""
        return self.getrawsampbit() // 8

    def setnchannels(self, nchannels):
        """Sets the number of channels of the current device."""
        if self._audio is None:
            raise RuntimeError('driver must be loaded')
        if nchannels <= 0:
            raise ValueError('nchannels >= 1 is required')
        flag = _spaudio_c.spSetAudioChannel(self._audio, nchannels)
        if not flag:
            raise DriverError('audio driver error')

    def getnchannels(self):
        """Gets the number of channels of the current device."""
        if self._audio is None:
            raise RuntimeError('driver must be loaded')
        flag, nchannels = _spaudio_c.spGetAudioChannel(self._audio)
        if flag:
            return nchannels
        else:
            raise DriverError('audio driver error')

    def setbuffersize(self, buffersize):
        """Sets the buffer size of the current device."""
        if self._audio is None:
            raise RuntimeError('driver must be loaded')
        flag = _spaudio_c.spSetAudioBufferSize(self._audio, buffersize)
        if not flag:
            raise DriverError('audio driver error')

    def getbuffersize(self):
        """Gets the buffer size of the current device."""
        if self._audio is None:
            raise RuntimeError('driver must be loaded')
        flag, buffersize = _spaudio_c.spGetAudioBufferSize(self._audio)
        if flag:
            return buffersize
        else:
            raise DriverError('audio driver error')

    def setnbuffers(self, nbuffers):
        """Sets the number of buffers of the current device."""
        if self._audio is None:
            raise RuntimeError('driver must be loaded')
        if nbuffers <= 0:
            raise ValueError('nbuffers >= 1 is required')
        flag = _spaudio_c.spSetAudioNumBuffer(self._audio, nbuffers)
        if not flag:
            raise DriverError('audio driver error')

    def getnbuffers(self):
        """Gets the number of buffers of the current device."""
        if self._audio is None:
            raise RuntimeError('driver must be loaded')
        flag, nbuffers = _spaudio_c.spGetAudioNumBuffer(self._audio)
        if flag:
            return nbuffers
        else:
            raise DriverError('audio driver error')

    def setblockingmode(self, mode):
        """Sets the blocking mode of the current device.

        Args:
            mode (int): 0 = blocking mode (default), 1 = nonblocking mode."""
        if self._audio is None:
            raise RuntimeError('driver must be loaded')
        flag = _spaudio_c.spSetAudioBlockingMode(self._audio, mode)
        if not flag:
            raise DriverError('audio driver error')

    def getblockingmode(self):
        """Gets the blocking mode of the current device.

        Returns:
            int: 0 = blocking mode (default), 1 = nonblocking mode.
        """
        if self._audio is None:
            raise RuntimeError('driver must be loaded')
        flag, mode = _spaudio_c.spGetAudioBlockingMode(self._audio)
        if flag:
            return mode
        else:
            raise DriverError('audio driver error')

    def getcomptype(self, decodebytes=False):
        """Returns compression type. Currently, ``'NONE'`` (decodebytes = ``True``)
        or ``b'NONE'`` (decodebytes = ``False``) will be returned."""
        if decodebytes:
            return 'NONE'
        else:
            return b'NONE'

    def getcompname(self, decodebytes=False):
        """Returns human-readable name of compression type. Currently,
        ``'not compressed'`` (decodebytes = ``True``) or ``b'not compressed'``
        (decodebytes = ``False``) will be returned.
        """
        if decodebytes:
            return 'not compressed'
        else:
            return b'not compressed'

    def setcomptype(self, encodestr=True):
        """Sets compression type. This parameter is ignored."""
        pass

    def setparams(self, params):
        """Sets supported all parameters described in dict or
        namedtuple object to the device.

        Args:
            params (dict): a dict object of parameters whose keys are
                ``'nchannels'``, ``'sampbit'``, ``'samprate'``,
                ``'blockingmode'``, ``'buffersize'``, or ``'nbuffers'``.
                The namedtuple generated by standard libraries
                such as aifc, wave, or sunau is also acceptable.
        """
        if self._audio is None:
            raise RuntimeError('driver must be loaded')
        # if isinstance(params, namedtuple):
        if _isnamedtupleinstance(params):
            # some versions of Python include _asdist() bug.
            params = dict(zip(params._fields, params))
        elif isinstance(params, tuple):
            params = dict(zip(_STANDARD_LIB_KEYS, params))
        sampbit = 0
        for key, value in params.items():
            if key == 'sampwidth':
                if sampbit == 0:
                    sampbit = value * 8
            elif key == 'sampbit':
                sampbit = value
            elif key == 'nchannels':
                self.setnchannels(value)
            elif key in ('samprate', 'framerate'):
                self.setsamprate(value)
            elif key == 'blockingmode':
                self.setblockingmode(value)
            elif key == 'buffersize':
                self.setbuffersize(value)
            elif key == 'nbuffers':
                self.setnbuffers(value)
        if sampbit > 0:
            self.setsampbit(sampbit)

    def getparams(self):
        """Gets supported all parameters of the current device in dict object.

        Returns:
            dict: A dict object including all parameters of the current device
            whose keys are ``'nchannels'``, ``'sampbit'``, ``'samprate'``,
            ``'blockingmode'``, ``'buffersize'``, and ``'nbuffers'``.
        """
        return dict(nchannels=self.getnchannels(), sampbit=self.getsampbit(),
                    samprate=self.getsamprate(), blockingmode=self.getblockingmode(),
                    buffersize=self.getbuffersize(), nbuffers=self.getnbuffers(),
                    sampwidth=self.getrawsampwidth(), framerate=self.getframerate())

    def getparamstuple(self, decodebytes=False, nframes=0):
        """Gets supported all parameters of the current device in namedtuple object.

        Args:
            decodebytes (bool, optional): ``True`` decodes bytes objects into
                string objects for ``'comptype'`` and ``'compname'``.
                The standard libraries of wave and sunau expect a decoded
                string object while the standard aifc library expects
                a bytes object.
            nframes (int, optional): Specify the number of frames of an audio
                file, otherwise 4th element of the output tuple will be 0.

        Returns:
            namedtuple: A namedtuple object including all parameters of
            the current device whose entries are
            ``(nchannels, sampwidth, framerate, nframes, comptype, compname)`` .
            This object is compatible with the argument of ``setparams()``
            of standard libraries such as aifc, wave, or sunau.
        """
        return _StandardLibParams(self.getnchannels(), self.getsampwidth(),
                                  self.getframerate(), nframes,
                                  self.getcomptype(decodebytes),
                                  self.getcompname(decodebytes))

    def _checksecondopen(self, mode):
        if (mode[0] == 'w' and self._read_mode[0] == 'r') \
           or (mode[0] == 'r' and self._write_mode[0] == 'w'):
            raise RuntimeError('cannot set parameters in 2nd open call')

    def open(self, mode, *, callback=None, deviceindex=-1, samprate=0,
             sampbit=0, nchannels=0, blockingmode=-1, buffersize=0,
             nbuffers=0, params=None):
        """Opens the current audio device.

        Args:
            mode (str): Device opening mode. ``'r'`` means read mode, ``'w'``
                means write mode. ``'ro'`` and ``'wo'`` which mean read only
                and write only modes are also supported. Although these modes
                validate only the specified mode, some environments recieve
                a benefit that the processing becomes faster.
            callback (tuple, optional): The callback function included in tuple
                which contains all arguments for
                :func:`~spaudio.SpAudio.setcallback` method.
            deviceindex (int, optional): The index of the audio device.
            samprate (double, optional): Sample rate of the device.
            sampbit (int, optional): Bits/sample of the device.
            nchannels (int, optional): The number of channels of the device.
            blockingmode (int, optional): 0 = blocking mode (default),
                1 = nonblocking mode.
            buffersize (int, optional): The buffer size of the device.
            nbuffers (int, optional): The number of buffers of the device.
            params (dict, optional): A dict object which can contain any
                above parameters from `samprate` to `nbuffers`.

        Note:
            Support for the keyword arguments was added in Version 0.7.15.
        """
        if self._audio is None:
            raise RuntimeError('driver must be loaded')

        if callback is not None:
            if isinstance(callback, tuple):
                self.setcallback(*callback)
            else:
                self.setcallback(OUTPUT_POSITION_CALLBACK | OUTPUT_BUFFER_CALLBACK,
                                 callback, None)
        if params is not None:
            self._checksecondopen(mode)
            self.setparams(params)
        if deviceindex != -1:
            self._checksecondopen(mode)
            self.selectdevice(deviceindex)
        if samprate != 0:
            self._checksecondopen(mode)
            self.setsamprate(samprate)
        if sampbit != 0:
            self._checksecondopen(mode)
            self.setsampbit(sampbit)
        if nchannels != 0:
            self._checksecondopen(mode)
            self.setnchannels(nchannels)
        if blockingmode != -1:
            self._checksecondopen(mode)
            self.setblockingmode(blockingmode)
        if buffersize != 0:
            self._checksecondopen(mode)
            self.setbuffersize(buffersize)
        if nbuffers != 0:
            self._checksecondopen(mode)
            self.setnbuffers(nbuffers)

        if mode[0] == 'r':
            if self._write_mode[-1] == 'o':
                raise RuntimeError('device has been opened with write only mode')
            elif self._read_mode[0] == 'r':
                raise RuntimeError('device has already been opened')
            self._read_mode = mode
        elif mode[0] == 'w':
            if self._read_mode[-1] == 'o':
                raise RuntimeError('device has been opened with read only mode')
            elif self._write_mode[0] == 'w':
                raise RuntimeError('device has already been opened')
            self._write_mode = mode
        else:
            raise RuntimeError('unknown open mode: %s' % mode)

        global _ischarbinary
        if _ischarbinary:
            mode2 = mode.encode('utf-8')
        else:
            mode2 = mode
        flag = _spaudio_c.spOpenAudioDevice(self._audio, mode2)
        if not flag:
            raise DeviceError('cannot open audio device')

    def close(self):
        """Closes the current audio device."""
        if self._audio is None:
            raise RuntimeError('driver must be loaded')
        flag = _spaudio_c.spCloseAudioDevice(self._audio)
        self._read_mode = ' '
        self._write_mode = ' '
        if not flag:
            raise DeviceError('cannot close audio device')

    def stop(self):
        """Stops audio I/O."""
        if self._audio is None:
            raise RuntimeError('driver must be loaded')
        flag = _spaudio_c.spStopAudio(self._audio)
        if not flag:
            raise DeviceError('cannot stop audio I/O')

    def sync(self):
        """Synchronizes audio I/O."""
        if self._audio is None:
            raise RuntimeError('driver must be loaded')
        flag = _spaudio_c.spSyncAudio(self._audio)
        if not flag:
            raise DeviceError('cannot synchronize audio I/O')

    def getrawarraytypecode(self):
        """Gets the type code for python array to store raw data.

        Returns:
            char: A type code for the current settings.
        """
        sampbit = self.getrawsampbit()
        if sampbit >= 64:
            typecode = 'd'
        elif sampbit >= 33:
            typecode = 'f'
        elif sampbit > 16:  # sampbit >= 32
            typecode = 'l'
        else:
            typecode = 'h'
        return typecode

    def createrawarray(self, length, nframesflag=False):
        """Creates a raw array for the current device settings.

        Args:
            length: A length of the array. Note that this length is
                not identical to the number of frames
                (length = nframes * nchannels).
                If you want to specify the number of frames,
                the second argument must be ``True``.
            nframesflag (bool, optional): ``True`` makes the first argument
                be treated as the number of frames.

        Returns:
            array.array: An array class object for the current device settings.
        """
        if nframesflag:
            length = int(length) * self.getnchannels()
        size = int(length) * self.getrawsampwidth()
        buffer = bytearray(size)
        return array.array(self.getrawarraytypecode(), buffer)

    def getarraytypecode(self):
        """Gets the type code for python array to store double-precision data.

        Returns:
            char: A type code of a double-precision array for the current settings.
        """
        return 'd'

    def createarray(self, length, nframesflag=False):
        """Creates a double-precision array for the current device settings.

        Args:
            length: A length of the array. Note that this length is
                not identical to the number of frames
                (length = nframes * nchannels).
                If you want to specify the number of frames,
                the second argument must be ``True``.
            nframesflag (bool, optional): ``True`` makes the first argument
                be treated as the number of frames.

        Returns:
            array.array: An array class object for the current device settings.
        """
        if nframesflag:
            length = int(length) * self.getnchannels()
        size = int(length) * 8
        buffer = bytearray(size)
        return array.array(self.getarraytypecode(), buffer)

    def getrawndarraydtype(self):
        """Gets the dtype string for numpy ndarray to store raw data.

        Returns:
            string: A dtype string for the current settings.
        """
        sampbit = self.getrawsampbit()
        if sampbit >= 64:
            dtypestr = 'f8'
        elif sampbit >= 33:
            dtypestr = 'f4'
        elif sampbit > 16:  # sampbit >= 32
            dtypestr = 'i4'
        else:
            dtypestr = 'i2'
        return dtypestr

    def createrawndarray(self, length, nframesflag=False, channelwise=False):
        """Creates a raw numpy ndarray for the current device settings.

        Args:
            length: A length of the array. Note that this length is
                not identical to the number of frames
                (length = nframes * nchannels).
                If you want to specify the number of frames,
                the second argument must be ``True``.
            nframesflag (bool, optional): ``True`` makes the first argument
                be treated as the number of frames.
            channelwise (bool, optional): ``True`` resizes the returned array
                into (nframes, nchannels) matrix.
                This argument is introduced in Version 0.7.16.

        Returns:
            numpy.ndarray: An ndarray class object for the current device
            settings.
        """
        import numpy as np
        nchannels = self.getnchannels()
        if nframesflag:
            nframes = int(length)
            length = nframes * nchannels
        else:
            length = int(length)
            nframes = length // nchannels
        size = length * self.getrawsampwidth()
        buffer = bytearray(size)
        oarray = np.frombuffer(buffer, dtype=self.getrawndarraydtype())
        if channelwise:
            oarray.resize((nframes, nchannels))
        return oarray

    def getndarraydtype(self):
        """Gets the dtype string for numpy ndarray to store double-precision data.

        Returns:
            string: A dtype string for the current settings.
        """
        return 'f8'

    def createndarray(self, length, nframesflag=False, channelwise=False):
        """Creates a numpy double-precision array for the current device settings.

        Args:
            length: A length of the array. Note that this length is
                not identical to the number of frames
                (length = nframes * nchannels).
                If you want to specify the number of frames,
                the second argument must be ``True``.
            nframesflag (bool, optional): ``True`` makes the first argument
                be treated as the number of frames.
            channelwise (bool, optional): ``True`` resizes the returned array
                into (nframes, nchannels) matrix.
                This argument is introduced in Version 0.7.16.

        Returns:
            numpy.ndarray: An ndarray class object for the current device
            settings.
        """
        import numpy as np
        nchannels = self.getnchannels()
        if nframesflag:
            nframes = int(length)
            length = nframes * nchannels
        else:
            length = int(length)
            nframes = length // nchannels
        size = length * 8
        buffer = bytearray(size)
        oarray = np.frombuffer(buffer, dtype=self.getndarraydtype())
        if channelwise:
            oarray.resize((nframes, nchannels))
        return oarray

    def readraw(self, data, offset=0, length=0):
        """Reads raw data from the audio device.

        Args:
            data (bytearray, array.array or numpy.ndarray):
                A raw array to receive raw data from the audio device.
            offset (int, optional): Optional offset location for the array.
            length (int, optional): Optional read length for the array.

        Returns:
            int: The read size if successful, -1 otherwise.

        Note:
            The keyword arguments of `offset` and `length` were
            introduced in Version 0.7.15.
        """
        if self._audio is None:
            raise RuntimeError('driver must be loaded')
        if data is None or len(data) <= 0:
            raise ValueError('a valid buffer must be specified')
        if self._read_mode[0] != 'r':
            raise RuntimeError('device must be opened with read mode')
        if isinstance(data, bytearray):
            buffer = data
        elif isinstance(data, array.array):
            buffer = memoryview(data)
        elif type(data).__name__ == 'ndarray':
            import numpy as np
            buffer = data.data
        else:
            raise RuntimeError('unsupported data type')

        offsetbyte = int(offset) * self.getrawsampwidth() if offset > 0 else 0
        lengthbyte = int(length) * self.getrawsampwidth() if length > 0 else 0

        nread = _spaudio_c.spReadAudioBuffer_(self._audio, buffer,
                                              offsetbyte, lengthbyte)
        return nread // self.getrawsampwidth() if nread > 0 else nread

    def writeraw(self, data, offset=0, length=0):
        """Writes data of a raw array to the audio device.

        Args:
            data (bytearray, array.array or numpy.ndarray):
                A raw array to send data to the audio device.
            offset (int, optional): Optional offset location for the array.
            length (int, optional): Optional write length for the array.

        Returns:
            int: The written size if successful, -1 otherwise.

        Note:
            The keyword arguments of `offset` and `length` were
            introduced in Version 0.7.15.
        """
        if self._audio is None:
            raise RuntimeError('driver must be loaded')
        if data is None or len(data) <= 0:
            raise ValueError('a valid buffer must be specified')
        if self._write_mode[0] != 'w':
            raise RuntimeError('device must be opened with write mode')
        if isinstance(data, (bytearray, bytes)):
            buffer = data
        elif isinstance(data, array.array):
            buffer = memoryview(data)
        elif type(data).__name__ == 'ndarray':
            import numpy as np
            buffer = data.data
        else:
            raise RuntimeError('unsupported data type')

        offsetbyte = int(offset) * self.getrawsampwidth() if offset > 0 else 0
        lengthbyte = int(length) * self.getrawsampwidth() if length > 0 else 0

        nwrite = _spaudio_c.spWriteAudioBuffer_(self._audio, buffer,
                                                offsetbyte, lengthbyte)
        return nwrite // self.getrawsampwidth() if nwrite > 0 else nwrite

    def read(self, data, weight=1.0, offset=0, length=0):
        """Reads data to a double-precision array from the audio device.

        Args:
            data (bytearray, array.array or numpy.ndarray):
                A double-precision array to receive data from the audio device.
            weight (double, optional): A weighting factor multiplied
                to data after reading.
            offset (int, optional): Optional offset location for the array.
            length (int, optional): Optional read length for the array.

        Returns:
            int: The read size if successful, -1 otherwise.

        Note:
            The keyword arguments of `offset` and `length` were
            introduced in Version 0.7.15.
        """
        if self._audio is None:
            raise RuntimeError('driver must be loaded')
        if data is None or len(data) <= 0:
            raise ValueError('a valid buffer must be specified')
        if self._read_mode[0] != 'r':
            raise RuntimeError('device must be opened with read mode')
        if isinstance(data, bytearray):
            buffer = data
        elif isinstance(data, array.array):
            if data.typecode != 'd':
                raise RuntimeError('the typecode must be \'d\'')
            buffer = memoryview(data)
        elif type(data).__name__ == 'ndarray':
            import numpy as np
            if not np.issubdtype('f8', data.dtype):
                raise RuntimeError('the dtype must be \'f8\' (\'float64\')')
            buffer = data.data
        else:
            raise RuntimeError('unsupported data type')
        return _spaudio_c.spReadAudioDoubleBufferWeighted_(self._audio, buffer,
                                                           weight, offset, length)

    def write(self, data, weight=1.0, offset=0, length=0):
        """Writes data of a double-precision array to the audio device.

        Args:
            data (bytearray, array.array or numpy.ndarray):
                A double-precision array to send data to the audio device.
            weight (double, optional): A weighting factor multiplied
                to data before writing.
            offset (int, optional): Optional offset location for the array.
            length (int, optional): Optional write length for the array.

        Returns:
            int: The written size if successful, -1 otherwise.

        Note:
            The keyword arguments of `offset` and `length` were
            introduced in Version 0.7.15.
        """
        if self._audio is None:
            raise RuntimeError('driver must be loaded')
        if data is None or len(data) <= 0:
            raise ValueError('a valid buffer must be specified')
        if self._write_mode[0] != 'w':
            raise RuntimeError('device must be opened with write mode')
        if isinstance(data, (bytearray, bytes)):
            buffer = data
        elif isinstance(data, array.array):
            if data.typecode != 'd':
                raise RuntimeError('the typecode must be \'d\'')
            buffer = memoryview(data)
        elif type(data).__name__ == 'ndarray':
            import numpy as np
            if not np.issubdtype('f8', data.dtype):
                raise RuntimeError('the dtype must be \'f8\' (\'float64\')')
            buffer = data.data
        else:
            raise RuntimeError('unsupported data type')
        return _spaudio_c.spWriteAudioDoubleBufferWeighted_(self._audio, buffer,
                                                            weight, offset, length)

    def readframes(self, nframes, weight=1.0, arraytype='ndarray',
                   channelwise=False):
        """Reads and returns the next `nframes` data of a double-precision array.

        Args:
            nframes (int): The number of frames to read.
            weight (double, optional): A weighting factor multiplied
                to data after reading.
            arraytype (str, optional): The type of output array. The value must
                be ``'ndarray'`` (default), ``'array'``, or ``'bytearray'``.
            channelwise (bool, optional): ``True`` resizes the returned ndarray
                into (nframes, nchannels) matrix.
                This argument is valid only in ``arraytype='ndarray'`` case.

        Returns:
            numpy.ndarray, array.array or bytearray: The output array object
            containing read data.

        Note:
            This function was introduced in Version 0.7.16.
        """
        if nframes <= 0:
            raise RuntimeError('invalid nframes value')

        length = int(nframes) * self.getnchannels()
        if arraytype in ('ndarray', 'numpy.ndarray'):
            data = self.createndarray(length, channelwise=channelwise)
        elif arraytype in ('array', 'array.array'):
            data = self.createarray(length)
        elif arraytype == 'bytearray':
            data = bytearray(length * 8)
        else:
            raise RuntimeError('unknown arraytype: %s' % arraytype)

        nread = self.read(data, weight=weight)
        if nread != length:
            warnings.warn('The read length (%d) is different from the buffer length (%d)'
                          % (nread, length))

        return data

    def readrawframes(self, nframes, arraytype='ndarray', channelwise=False):
        """Reads and returns the next `nframes` data of a raw array.

        Args:
            nframes (int): The number of frames to read.
            arraytype (str, optional): The type of output array. The value must
                be ``'ndarray'`` (default), ``'array'``, or ``'bytearray'``.
            channelwise (bool, optional): ``True`` resizes the returned ndarray
                into (nframes, nchannels) matrix.
                This argument is valid only in ``arraytype='ndarray'`` case.

        Returns:
            numpy.ndarray, array.array or bytearray: The output array object
            containing read data.

        Note:
            This function was introduced in Version 0.7.16.
        """
        if nframes <= 0:
            raise RuntimeError('invalid nframes value')

        length = int(nframes) * self.getnchannels()
        if arraytype in ('ndarray', 'numpy.ndarray'):
            data = self.createrawndarray(length, channelwise=channelwise)
        elif arraytype in ('array', 'array.array'):
            data = self.createrawarray(length)
        elif arraytype == 'bytearray':
            data = bytearray(length * self.getrawsampwidth())
        else:
            raise RuntimeError('unknown arraytype: %s' % arraytype)

        nread = self.readraw(data)
        if nread != length:
            warnings.warn('The read length (%d) is different from the buffer length (%d)'
                          % (nread, length))

        return data

    def writeframes(self, data, weight=1.0):
        """Writes data of a double-precision array to the audio device.

        Args:
            data (bytearray, array.array or numpy.ndarray):
                A double-precision array to send data to the audio device.
            weight (double, optional): A weighting factor multiplied
                to data before writing.

        Returns:
            int: The written number of frames if successful, -1 otherwise.

        Note:
            This function was introduced in Version 0.7.16.
        """
        nwrite = self.write(data, weight=weight)
        if nwrite > 0:
            nwrite = nwrite // self.getnchannels()
        return nwrite

    def writerawframes(self, data):
        """Writes data of a raw array to the audio device.

        Args:
            data (bytearray, array.array or numpy.ndarray):
                A raw array to send data to the audio device.

        Returns:
            int: The written number of frames if successful, -1 otherwise.

        Note:
            This function was introduced in Version 0.7.16.
        """
        nwrite = self.writeraw(data)
        if nwrite > 0:
            nwrite = nwrite // self.getnchannels()
        return nwrite


def getndrivers():
    """Gets the number of drivers."""
    return _spaudio_c.spGetNumAudioDriver()


def getdrivername(index):
    """Gets the name of the driver which has the index specified.

    Args:
        index (int): The index associated with the audio driver.

    Returns:
        string: A string containing the driver name.

    Raises:
        ValueError: If `index` is greater than or equal to
            the number of drivers.
    """
    if index < 0 or index >= getndrivers():
        raise ValueError('0 <= index < %d is required'
                         % getndrivers())
    name = _spaudio_c.xspGetAudioDriverName(index)
    if name is not None:
        global _ischarbinary
        if _ischarbinary:
            return name.decode(locale.getpreferredencoding())
        else:
            return name
    else:
        raise DriverError('audio driver error')


def getdriverlist():
    """Gets a list of driver names."""
    alist = []
    for i in range(getndrivers()):
        alist.append(getdrivername(i))
    return alist


def getndriverdevices(drivername=None):
    """Gets the number of devices in the driver."""
    if drivername is not None:
        global _ischarbinary
        if _ischarbinary:
            encodedname = drivername.encode(locale.getpreferredencoding())
        else:
            encodedname = drivername
    else:
        encodedname = None
    return _spaudio_c.spGetNumAudioDriverDevice(encodedname)


def getdriverdevicename(index, drivername=None):
    """Gets the name of the device in the driver.

    Args:
        index (int): The index associated with the audio device.
        drivername (str): Optional driver name.

    Returns:
        string: A string containing the device name.

    Raises:
        ValueError: If `index` is greater than or equal to
            the number of devices.
    """
    global _ischarbinary
    if index < 0 or index >= getndriverdevices(drivername):
        raise ValueError('0 <= index < %d is required'
                         % getndriverdevices(drivername))
    if drivername is not None:
        if _ischarbinary:
            encodedname = drivername.encode(locale.getpreferredencoding())
        else:
            encodedname = drivername
    else:
        encodedname = None
    devicename = _spaudio_c.xspGetAudioDriverDeviceName(encodedname, index)
    if devicename is not None:
        if _ischarbinary:
            return devicename.decode(locale.getpreferredencoding())
        else:
            return devicename
    else:
        return ''


def open(mode, *, drivername=None, callback=None, deviceindex=-1, samprate=0,
         sampbit=0, nchannels=0, blockingmode=-1, buffersize=0, nbuffers=0,
         params=None):
    """Opens an audio device. This function may be used in a ``with`` statement.

    Args:
        mode (str): Device opening mode. ``'r'`` means read mode, ``'w'``
            means write mode. ``'ro'`` and ``'wo'`` which mean read only
            and write only modes are also supported. Although these modes
            validate only the specified mode, some environments recieve
            a benefit that the processing becomes faster.
            In this function, ``'rw'`` which means open with ``'w'``
            after ``'r'`` is also supported.
        drivername (str, optional): The driver name to initialize.
        callback (tuple, optional): The callback function included in
            tuple which contains all arguments for
            :func:`~spaudio.SpAudio.setcallback` method.
        deviceindex (int, optional): The index of the audio device.
        samprate (double, optional): Sample rate of the device.
        sampbit (int, optional): Bits/sample of the device.
        nchannels (int, optional): The number of channels of the device.
        blockingmode (int, optional): 0 = blocking mode (default),
            1 = nonblocking mode.
        buffersize (int, optional): The buffer size of the device.
        nbuffers (int, optional): The number of buffers of the device.
        params (dict, optional): A dict object which can contain any
            above parameters from `samprate` to `nbuffers`.

    Returns:
        SpAudio: A new instance of :class:`~spaudio.SpAudio` class.

    Note:
        This function was introduced in Version 0.7.15.
    """
    audio = SpAudio(drivername)

    if mode[0] == 'r':
        modefirst = 'ro' if mode[1] == 'o' else 'r'
    elif mode[0] == 'w':
        modefirst = 'wo' if mode[1] == 'o' else 'w'
    else:
        raise RuntimeError('unknown open mode: %s' % mode)

    modesecond = None
    if mode[0] == 'w':
        if mode[1] == 'r':
            modesecond = 'r'
        elif mode[1] != 'o':
            raise RuntimeError('unknown open mode: %s' % mode)
    elif mode[0] == 'r':
        if mode[1] == 'w':
            modesecond = 'w'
        elif mode[1] != 'o':
            raise RuntimeError('unknown open mode: %s' % mode)

    audio.open(modefirst, callback=callback, deviceindex=deviceindex,
               samprate=samprate, sampbit=sampbit, nchannels=nchannels,
               blockingmode=blockingmode, buffersize=buffersize,
               nbuffers=nbuffers, params=params)
    if modesecond is not None:
        audio.open(modesecond)

    return audio


if __name__ == '__main__':
    driverlist = getdriverlist()
    for i in range(getndrivers()):
        print('Driver %d: %s' % (i, driverlist[i]))
        for j in range(getndriverdevices(driverlist[i])):
            print('    Device %d: %s'
                  % (j, getdriverdevicename(j, driverlist[i])))
