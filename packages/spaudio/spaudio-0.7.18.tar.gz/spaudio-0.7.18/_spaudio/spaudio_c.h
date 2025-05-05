extern int spSetAudioCallbackFunc_(spAudio audio, spAudioCallbackType call_type, PyObject *obj);

extern long spReadAudioBuffer_(spAudio audio, char *buffer, long buf_size, long offset_byte, long length_byte);
extern long spWriteAudioBuffer_(spAudio audio, char *buffer, long buf_size, long offset_byte, long length_byte);

extern long spReadAudioDoubleBufferWeighted_(spAudio audio, char *buffer, long buf_size, double weight,
                                             long offset, long length);

extern long spWriteAudioDoubleBufferWeighted_(spAudio audio, char *buffer, long buf_size, double weight,
                                              long offset, long length);
