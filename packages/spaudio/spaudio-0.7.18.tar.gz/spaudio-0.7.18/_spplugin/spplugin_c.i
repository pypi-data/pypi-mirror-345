%module spplugin_c
%begin %{
#define SWIG_PYTHON_STRICT_BYTE_CHAR
%}
%include <typemaps.i>
%include <pybuffer.i>
%include <cstring.i>

%{
#include <sp/spBase.h>
#include <sp/spWave.h>
#include <sp/spPlugin.h>
#include <sp/spOutputPlugin.h>
#include <sp/spInputPlugin.h>
#include "spplugin_c.h"
%}

#if defined(_WIN64)
#define spLong __int64
#else /* defined(_WIN64) */
#define spLong long
#endif

typedef int spBool;
typedef struct _spPlugin spPlugin;
typedef int spPluginError;

/** The callback reason for the plugin callback function. */
typedef enum {
    SP_PLUGIN_CR_NONE = -1,
    SP_PLUGIN_CR_ERROR = 0,     /**< Callbacked for an error.  */
    SP_PLUGIN_CR_OPTION = 1,    /**< Callbacked when the options must be updated. host_data: spOptions */
} spPluginCallbackReason;

typedef spBool (*spPluginOpenCallback)(spPlugin *plugin, spPluginCallbackReason reason, void *host_data, void *call_data);

/** Target device of the plugin. */
typedef enum {
    SP_PLUGIN_DEVICE_UNKNOWN = -1, /**< Unknow target. */
    SP_PLUGIN_DEVICE_FILE = 0,     /**< A file. */
    SP_PLUGIN_DEVICE_AUDIO = 1,    /**< An audio device. */
    SP_PLUGIN_DEVICE_CD = 2,       /**< A CD player.  */
    SP_PLUGIN_DEVICE_MIXER = 3,    /**< A mixer device. */
    SP_PLUGIN_DEVICE_OTHERS = 4,   /**< Other devices. */
} spPluginDeviceType;

typedef struct _spWaveInfo {
    char file_type[SP_WAVE_FILE_TYPE_SIZE];     /**< @~english Format unique ID, e.g. `"wav"` . */
    char file_desc[SP_WAVE_FILE_DESC_SIZE];     /**< @~english Format description, e.g. `"Microsoft PCM"` . */
    char file_filter[SP_WAVE_FILE_FILTER_SIZE]; /**< @~english Filter mask, e.g. `"*.wav"` . */
    int buffer_size;            /**< @~english Buffer size for output buffer. */
    spLong header_size;         /**< @~english You can skip header by fseek with this size. If you aren't allowed that, zero will be set. */
    int samp_bit;               /**< @~english Bits/sample. */
    int num_channel;            /**< @~english The number of channels. */
    double samp_rate;           /**< @~english Sampling rate [Hz]. */
    long bit_rate;              /**< @~english Bit rate [bits/sec]. */
    spLong length;              /**< @~english Total length of sound [point]. */
} spWaveInfo;

typedef struct _spSongInfo {
    unsigned long info_mask;            /**< @~english Mask indicating which information is valid. */
    spLong32 track;                     /**< @~english Track number. */
    char title[SP_SONG_INFO_SIZE];      /**< @~english Song title. */
    char artist[SP_SONG_INFO_SIZE];     /**< @~english Artist name. */
    char album[SP_SONG_INFO_SIZE];      /**< @~english Album title. */
    char genre[SP_SONG_INFO_SIZE];      /**< @~english Genre. */
    char release[SP_SONG_INFO_SIZE];    /**< @~english Release date. */
    char copyright[SP_SONG_INFO_SIZE];  /**< @~english Copyright information. */
    char engineer[SP_SONG_INFO_SIZE];   /**< @~english Engineer name. */
    char source[SP_SONG_INFO_SIZE];     /**< @~english Source information. WAVE file uses this information. */
    char software[SP_SONG_INFO_SIZE];   /**< @~english Software name. */
    char subject[SP_SONG_INFO_SIZE];    /**< @~english Subject. */
    char comment[SP_SONG_INFO_SIZE];    /**< @~english Some comments. */
} spSongInfo;

%typemap(newfree) char * "free($1);";
%newobject xspGetSongInfoStringField_;
%newobject xspGetWaveInfoStringField_;
extern char *xspGetSongInfoStringField_(spSongInfo *song_info, char *key);
extern char *xspGetWaveInfoStringField_(spWaveInfo *wave_info, int index);

%typemap(out) spBool {
    $result = PyInt_FromLong($1);
}
%typemap(out) spPluginError {
    $result = PyInt_FromLong($1);
}

extern const char *spGetDefaultDir(void);

extern spBool spInitWaveInfo(spWaveInfo *wave_info);
extern spBool spInitSongInfo(spSongInfo *song_info);

extern void spSetPluginSearchPath(const char *pathlist);
extern spBool spAppendPluginSearchPath(const char *pathlist);
extern const char *spSearchPluginFile(int index);

%newobject spLoadPlugin;
%delobject spFreePlugin;
extern spPlugin *spLoadPlugin(const char *plugin_name);
extern spBool spFreePlugin(spPlugin *plugin);
extern const char *spGetPluginName(spPlugin *plugin);
extern const char *spGetPluginId(spPlugin *plugin);
extern const char *spGetPluginDescription(spPlugin *plugin);
extern const char *spGetPluginInformation(spPlugin *plugin);
extern long spGetPluginVersionId(spPlugin *plugin);
extern spBool spGetPluginVersion(spPlugin *plugin, int *OUTPUT, int *OUTPUT);

%newobject spOpenFilePluginAuto_;
%delobject spCloseFilePlugin;
extern spPlugin *spOpenFilePluginAuto_(const char *plugin_name, const char *filename, const char *mode,
                                       spPluginDeviceType device_type, spWaveInfo *wave_info, spSongInfo *song_info,
                                       int *OUTPUT);
spBool spCloseFilePlugin(spPlugin *plugin);

extern spBool spSeekPlugin(spPlugin *plugin, spLong pos);

extern spBool spIsSongInfoNumberFieldKey_(char *key);
extern long spGetSongInfoNumberField_(spSongInfo *song_info, char *key);
extern void spUpdateSongInfoNumberField_(spSongInfo *song_info, char *key, long value);
extern void spUpdateSongInfoStringField_(spSongInfo *song_info, char *key, char *value);
extern void spSetWaveInfoFileType_(spWaveInfo *wave_info, char *file_type);

%pybuffer_binary(char *buffer, long buf_size);
extern long spWritePluginInByte_(spPlugin *plugin, char *buffer, long buf_size, long offset_byte, long length_byte);
extern long spWritePluginDoubleWeighted_(spPlugin *plugin, char *buffer, long buf_size, double weight,
                                         long offset, long length);

%pybuffer_mutable_binary(char *buffer, long buf_size);
extern long spReadPluginInByte_(spPlugin *plugin, char *buffer, long buf_size, long offset_byte, long length_byte);
extern long spReadPluginDoubleWeighted_(spPlugin *plugin, char *buffer, long buf_size, double weight,
                                        long offset, long length);

%pybuffer_binary(char *src_buffer, long src_buf_size);
%pybuffer_mutable_binary(char *dest_buffer, long dest_buf_size);
extern 
long spCopyBuffer_(char *dest_buffer, long dest_buf_size, int dest_samp_byte,
                   spBool dest_big_endian_or_signed8bit,
                   char *src_buffer, long src_buf_size, int src_samp_byte,
                   spBool src_big_endian_or_signed8bit, int mult2432);
