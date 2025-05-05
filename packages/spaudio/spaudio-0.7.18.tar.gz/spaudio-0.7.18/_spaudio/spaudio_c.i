%module spaudio_c
%begin %{
#define SWIG_PYTHON_STRICT_BYTE_CHAR
%}
%include <typemaps.i>
%include <pybuffer.i>

%{
#include <sp/spBase.h>
#include <sp/spAudio.h>
#include "spaudio_c.h"
%}

typedef int spBool;
typedef struct _spAudio *spAudio;
typedef unsigned long spAudioCallbackType;

%typemap(newfree) char * "free($1);";
%newobject xspGetAudioDriverName;
%newobject xspGetAudioDriverDeviceName;
%newobject xspGetAudioDeviceName;

%typemap(out) spBool {
    $result = PyInt_FromLong($1);
}
%typemap(in) spLong {
    $1 = PyLong_AsLong($input);
}
%typemap(out) spLong {
    $result = PyInt_FromLong($1);
}
%typemap(in) spAudioCallbackType {
    $1 = PyLong_AsUnsignedLong($input);
}
%typemap(out) spAudioCallbackType {
    $result = PyLong_FromUnsignedLong($1);
}

extern int spGetNumAudioDriver(void);
extern char *xspGetAudioDriverName(int index);

extern int spGetNumAudioDriverDevice(const char *driver_name);
extern char *xspGetAudioDriverDeviceName(const char *driver_name, int index);

%newobject spInitAudioDriver;
%delobject _spFreeAudioDriver;
extern spAudio spInitAudioDriver(const char *driver_name);
extern void _spFreeAudioDriver(spAudio audio);

extern char *xspGetAudioDeviceName(spAudio audio, int device_index);

extern spBool spSelectAudioDevice(spAudio audio, int device_index);
extern spBool spSetAudioSampleRate(spAudio audio, double samp_rate);
extern spBool spSetAudioChannel(spAudio audio, int num_channel);
extern spBool spSetAudioBufferSize(spAudio audio, int buffer_size);
extern spBool spSetAudioNumBuffer(spAudio audio, int num_buffer);
extern spBool spSetAudioBlockingMode(spAudio audio, int block_mode);
extern spBool spSetAudioSampleBit(spAudio audio, int samp_bit);

extern spBool spGetNumAudioDevice(spAudio audio, int *OUTPUT);
extern spBool spGetAudioSampleRate(spAudio audio, double *OUTPUT);
extern spBool spGetAudioChannel(spAudio audio, int *OUTPUT);
extern spBool spGetAudioBufferSize(spAudio audio, int *OUTPUT);
extern spBool spGetAudioNumBuffer(spAudio audio, int *OUTPUT);
extern spBool spGetAudioBlockingMode(spAudio audio, int *OUTPUT);
extern spBool spGetAudioSampleBit(spAudio audio, int *OUTPUT);
extern spBool spGetAudioSpecifiedSampleBit(spAudio audio, int *OUTPUT);
extern spBool spGetAudioOutputPosition(spAudio audio, spLong *OUTPUT);

extern spBool spOpenAudioDevice(spAudio audio, const char *mode);
extern spBool spCloseAudioDevice(spAudio audio);
extern spBool spStopAudio(spAudio audio);
extern spBool spSyncAudio(spAudio audio);

%pybuffer_binary(char *buffer, long buf_size);
extern long spWriteAudioBuffer_(spAudio audio, char *buffer, long buf_size, long offset_byte, long length_byte);
extern long spWriteAudioDoubleBufferWeighted_(spAudio audio, char *buffer, long buf_size, double weight,
                                              long offset, long length);

%pybuffer_mutable_binary(char *buffer, long buf_size);
extern long spReadAudioBuffer_(spAudio audio, char *buffer, long buf_size, long offset_byte, long length_byte);
extern long spReadAudioDoubleBufferWeighted_(spAudio audio, char *buffer, long buf_size, double weight,
                                             long offset, long length);

%include "spaudio_c.h"
