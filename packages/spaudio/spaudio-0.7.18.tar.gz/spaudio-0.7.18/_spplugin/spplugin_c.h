extern spBool spIsSongInfoNumberFieldKey_(char *key);
extern long spGetSongInfoNumberField_(spSongInfo *song_info, char *key);
extern void spUpdateSongInfoNumberField_(spSongInfo *song_info, char *key, long value);
extern char *xspGetSongInfoStringField_(spSongInfo *song_info, char *key);
extern void spUpdateSongInfoStringField_(spSongInfo *song_info, char *key, char *value);

extern char *xspGetWaveInfoStringField_(spWaveInfo *wave_info, int index);
extern void spSetWaveInfoFileType_(spWaveInfo *wave_info, char *file_type);

extern spPlugin *spOpenFilePluginAuto_(const char *plugin_name, const char *filename, const char *mode,
                                       spPluginDeviceType device_type, spWaveInfo *wave_info, spSongInfo *song_info,
                                       int *error);

extern long spReadPluginInByte_(spPlugin *plugin, char *buffer, long buf_size, long offset_byte, long length_byte);
extern long spReadPluginDoubleWeighted_(spPlugin *plugin, char *buffer, long buf_size, double weight,
                                        long offset, long length);
extern long spWritePluginInByte_(spPlugin *plugin, char *buffer, long buf_size, long offset_byte, long length_byte);
extern long spWritePluginDoubleWeighted_(spPlugin *plugin, char *buffer, long buf_size, double weight,
                                         long offset, long length);

extern 
long spCopyBuffer_(char *dest_buffer, long dest_buf_size, int dest_samp_byte,
                   spBool dest_big_endian_or_signed8bit,
                   char *src_buffer, long src_buf_size, int src_samp_byte,
                   spBool src_big_endian_or_signed8bit, int mult2432);
