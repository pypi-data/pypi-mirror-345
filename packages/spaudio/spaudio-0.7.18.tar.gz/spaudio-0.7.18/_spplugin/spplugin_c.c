#include <Python.h>

#include <sp/spBase.h>
#include <sp/spFile.h>
#include <sp/spMemory.h>
#include <sp/spThread.h>
#include <sp/spOutputPlugin.h>
#include <sp/spInputPlugin.h>
#include "spplugin_c.h"

spBool spIsSongInfoNumberFieldKey_(char *key)
{
    if (strcaseeq(key, "track")
        || strcaseeq(key, "track_total")
        || strcaseeq(key, "disc")
        || strcaseeq(key, "disc_total")
        || strcaseeq(key, "tempo")) {
        return SP_TRUE;
    } else {
        return SP_FALSE;
    }
}

long spGetSongInfoNumberField_(spSongInfo *song_info, char *key)
{
    long number = -1;
    spSongInfoV2 *song_info_v2 = (spSongInfoV2 *)song_info;
    
    if (strcaseeq(key, "track")) {
        if (song_info_v2->info_mask & SP_SONG_TRACK_MASK) {
            number = (long)song_info_v2->track;
        }
    } else if (strcaseeq(key, "track_total")) {
        if (song_info_v2->info_mask & SP_SONG_TRACK_TOTAL_MASK) {
            number = (long)song_info_v2->track_total;
        }
    } else if (strcaseeq(key, "disc")) {
        if (song_info_v2->info_mask & SP_SONG_DISC_MASK) {
            number = (long)song_info_v2->disc;
        }
    } else if (strcaseeq(key, "disc_total")) {
        if (song_info_v2->info_mask & SP_SONG_DISC_TOTAL_MASK) {
            number = (long)song_info_v2->disc_total;
        }
    } else if (strcaseeq(key, "tempo")) {
        if (song_info_v2->info_mask & SP_SONG_TEMPO_MASK) {
            number = (long)song_info_v2->tempo;
        }
    }

    return number;
}

void spUpdateSongInfoNumberField_(spSongInfo *song_info, char *key, long value)
{
    spSongInfoV2 *song_info_v2 = (spSongInfoV2 *)song_info;
    
    if (strcaseeq(key, "track")) {
        song_info_v2->info_mask |= SP_SONG_TRACK_MASK;
        song_info_v2->track = (spLong32)value;
    } else if (strcaseeq(key, "track_total")) {
        song_info_v2->info_mask |= SP_SONG_TRACK_TOTAL_MASK;
        song_info_v2->track_total = (spLong32)value;
    } else if (strcaseeq(key, "disc")) {
        song_info_v2->info_mask |= SP_SONG_DISC_MASK;
        song_info_v2->disc = (spLong32)value;
    } else if (strcaseeq(key, "disc_total")) {
        song_info_v2->info_mask |= SP_SONG_DISC_TOTAL_MASK;
        song_info_v2->disc_total = (spLong32)value;
    } else if (strcaseeq(key, "tempo")) {
        song_info_v2->info_mask |= SP_SONG_TEMPO_MASK;
        song_info_v2->tempo = (spLong32)value;
    }
}

char *xspGetSongInfoStringField_(spSongInfo *song_info, char *key)
{
    spSongInfoV2 *song_info_v2 = (spSongInfoV2 *)song_info;
    
    if (strcaseeq(key, "title")) {
        if (song_info_v2->info_mask & SP_SONG_TITLE_MASK) {
            return xspStrClone(song_info_v2->title);
        }
    } else if (strcaseeq(key, "artist")) {
        if (song_info_v2->info_mask & SP_SONG_ARTIST_MASK) {
            return xspStrClone(song_info_v2->artist);
        }
    } else if (strcaseeq(key, "album")) {
        if (song_info_v2->info_mask & SP_SONG_ALBUM_MASK) {
            return xspStrClone(song_info_v2->album);
        }
    } else if (strcaseeq(key, "genre")) {
        if (song_info_v2->info_mask & SP_SONG_GENRE_MASK) {
            return xspStrClone(song_info_v2->genre);
        }
    } else if (strcaseeq(key, "release")) {
        if (song_info_v2->info_mask & SP_SONG_RELEASE_MASK) {
            return xspStrClone(song_info_v2->release);
        }
    } else if (strcaseeq(key, "copyright")) {
        if (song_info_v2->info_mask & SP_SONG_COPYRIGHT_MASK) {
            return xspStrClone(song_info_v2->copyright);
        }
    } else if (strcaseeq(key, "engineer")) {
        if (song_info_v2->info_mask & SP_SONG_ENGINEER_MASK) {
            return xspStrClone(song_info_v2->engineer);
        }
    } else if (strcaseeq(key, "source")) {
        if (song_info_v2->info_mask & SP_SONG_SOURCE_MASK) {
            return xspStrClone(song_info_v2->source);
        }
    } else if (strcaseeq(key, "software")) {
        if (song_info_v2->info_mask & SP_SONG_SOFTWARE_MASK) {
            return xspStrClone(song_info_v2->software);
        }
    } else if (strcaseeq(key, "subject")) {
        if (song_info_v2->info_mask & SP_SONG_SUBJECT_MASK) {
            return xspStrClone(song_info_v2->subject);
        }
    } else if (strcaseeq(key, "comment")) {
        if (song_info_v2->info_mask & SP_SONG_COMMENT_MASK) {
            return xspStrClone(song_info_v2->comment);
        }
    } else if (strcaseeq(key, "album_artist")) { /* V2 only */
        if (song_info_v2->info_mask & SP_SONG_ALBUM_ARTIST_MASK) {
            return xspStrClone(song_info_v2->album_artist);
        }
    } else if (strcaseeq(key, "composer")) { /* V2 only */
        if (song_info_v2->info_mask & SP_SONG_COMPOSER_MASK) {
            return xspStrClone(song_info_v2->composer);
        }
    } else if (strcaseeq(key, "lyricist")) { /* V2 only */
        if (song_info_v2->info_mask & SP_SONG_LYRICIST_MASK) {
            return xspStrClone(song_info_v2->lyricist);
        }
    } else if (strcaseeq(key, "producer")) { /* V2 only */
        if (song_info_v2->info_mask & SP_SONG_PRODUCER_MASK) {
            return xspStrClone(song_info_v2->producer);
        }
    } else if (strcaseeq(key, "isrc")) { /* V2 only */
        if (song_info_v2->info_mask & SP_SONG_ISRC_MASK) {
            return xspStrClone(song_info_v2->isrc);
        }
    }

    return NULL;
}

void spUpdateSongInfoStringField_(spSongInfo *song_info, char *key, char *value)
{
    spSongInfoV2 *song_info_v2 = (spSongInfoV2 *)song_info;
    
    if (strcaseeq(key, "title")) {
        song_info_v2->info_mask |= SP_SONG_TITLE_MASK;
        spStrCopy(song_info_v2->title, sizeof(song_info_v2->title), value);
    } else if (strcaseeq(key, "artist")) {
        song_info_v2->info_mask |= SP_SONG_ARTIST_MASK;
        spStrCopy(song_info_v2->artist, sizeof(song_info_v2->artist), value);
    } else if (strcaseeq(key, "album")) {
        song_info_v2->info_mask |= SP_SONG_ALBUM_MASK;
        spStrCopy(song_info_v2->album, sizeof(song_info_v2->album), value);
    } else if (strcaseeq(key, "genre")) {
        song_info_v2->info_mask |= SP_SONG_GENRE_MASK;
        spStrCopy(song_info_v2->genre, sizeof(song_info_v2->genre), value);
    } else if (strcaseeq(key, "release")) {
        song_info_v2->info_mask |= SP_SONG_RELEASE_MASK;
        spStrCopy(song_info_v2->release, sizeof(song_info_v2->release), value);
    } else if (strcaseeq(key, "copyright")) {
        song_info_v2->info_mask |= SP_SONG_COPYRIGHT_MASK;
        spStrCopy(song_info_v2->copyright, sizeof(song_info_v2->copyright), value);
    } else if (strcaseeq(key, "engineer")) {
        song_info_v2->info_mask |= SP_SONG_ENGINEER_MASK;
        spStrCopy(song_info_v2->engineer, sizeof(song_info_v2->engineer), value);
    } else if (strcaseeq(key, "source")) {
        song_info_v2->info_mask |= SP_SONG_SOURCE_MASK;
        spStrCopy(song_info_v2->source, sizeof(song_info_v2->source), value);
    } else if (strcaseeq(key, "software")) {
        song_info_v2->info_mask |= SP_SONG_SOFTWARE_MASK;
        spStrCopy(song_info_v2->software, sizeof(song_info_v2->software), value);
    } else if (strcaseeq(key, "subject")) {
        song_info_v2->info_mask |= SP_SONG_SUBJECT_MASK;
        spStrCopy(song_info_v2->subject, sizeof(song_info_v2->subject), value);
    } else if (strcaseeq(key, "comment")) {
        song_info_v2->info_mask |= SP_SONG_COMMENT_MASK;
        spStrCopy(song_info_v2->comment, sizeof(song_info_v2->comment), value);
    } else if (strcaseeq(key, "album_artist")) { /* V2 only */
        song_info_v2->info_mask |= SP_SONG_ALBUM_ARTIST_MASK;
        spStrCopy(song_info_v2->album_artist, sizeof(song_info_v2->album_artist), value);
    } else if (strcaseeq(key, "composer")) { /* V2 only */
        song_info_v2->info_mask |= SP_SONG_COMPOSER_MASK;
        spStrCopy(song_info_v2->composer, sizeof(song_info_v2->composer), value);
    } else if (strcaseeq(key, "lyricist")) { /* V2 only */
        song_info_v2->info_mask |= SP_SONG_LYRICIST_MASK;
        spStrCopy(song_info_v2->lyricist, sizeof(song_info_v2->lyricist), value);
    } else if (strcaseeq(key, "producer")) { /* V2 only */
        song_info_v2->info_mask |= SP_SONG_PRODUCER_MASK;
        spStrCopy(song_info_v2->producer, sizeof(song_info_v2->producer), value);
    } else if (strcaseeq(key, "isrc")) { /* V2 only */
        song_info_v2->info_mask |= SP_SONG_ISRC_MASK;
        spStrCopy(song_info_v2->isrc, sizeof(song_info_v2->isrc), value);
    }
}

char *xspGetWaveInfoStringField_(spWaveInfo *wave_info, int index)
{
    if (index == 0) {
        return xspStrClone(wave_info->file_type);
    } else if (index == 1) {
        return xspStrClone(wave_info->file_desc);
    } else if (index == 2) {
        return xspStrClone(wave_info->file_filter);
    } else {
        return NULL;
    }
}

void spSetWaveInfoFileType_(spWaveInfo *wave_info, char *file_type)
{
    if (file_type == NULL || file_type[0] == NUL) {
        wave_info->file_type[0] = NUL;
        wave_info->file_desc[0] = NUL;
        wave_info->file_filter[0] = NUL;
    } else {
        spStrCopy(wave_info->file_type, sizeof(wave_info->file_type), file_type);
    }
}

spPlugin *spOpenFilePluginAuto_(const char *plugin_name, const char *filename, const char *mode,
                                spPluginDeviceType device_type, spWaveInfo *wave_info, spSongInfo *song_info,
                                int *error)
{
    int terror = 0;
    spPlugin *plugin;
    
    if ((plugin = spOpenFilePluginAuto(plugin_name, filename, mode, device_type,
                                       wave_info, song_info, NULL, NULL, &terror)) == NULL) {
        plugin = spAllocNullPlugin();
    }
    if (error != NULL) *error = terror;

    return plugin;
}

long spReadPluginInByte_(spPlugin *plugin, char *buffer, long buf_size, long offset_byte, long length_byte)
{
    if (length_byte <= 0) {
        length_byte = buf_size - offset_byte;
    } else {
        length_byte = MIN(length_byte, buf_size - offset_byte);
    }

    return spReadPluginInByte(plugin, buffer + offset_byte, length_byte);
}

long spReadPluginDoubleWeighted_(spPlugin *plugin, char *buffer, long buf_size, double weight,
                                 long offset, long length)
{
    long buf_length;
    long offset_byte;

    buf_length = buf_size / sizeof(double);
    offset_byte = offset * sizeof(double);
    
    if (length <= 0) {
        length = (buf_length - offset);
    } else {
        length = MIN(length, buf_length - offset);
    }
    
    return spReadPluginDoubleWeighted(plugin, (double *)(buffer + offset_byte), length, weight);
}

long spWritePluginInByte_(spPlugin *plugin, char *buffer, long buf_size, long offset_byte, long length_byte)
{
    if (length_byte <= 0) {
        length_byte = buf_size - offset_byte;
    } else {
        length_byte = MIN(length_byte, buf_size - offset_byte);
    }

    return spWritePluginInByte(plugin, buffer + offset_byte, length_byte);
}

long spWritePluginDoubleWeighted_(spPlugin *plugin, char *buffer, long buf_size, double weight,
                                  long offset, long length)
{
    long buf_length;
    long offset_byte;

    buf_length = buf_size / sizeof(double);
    offset_byte = offset * sizeof(double);
    
    if (length <= 0) {
        length = (buf_length - offset);
    } else {
        length = MIN(length, buf_length - offset);
    }
    
    return spWritePluginDoubleWeighted(plugin, (double *)(buffer + offset_byte), length, weight);
}

long spCopyBuffer_(char *dest_buffer, long dest_buf_size, int dest_samp_byte,
                   spBool dest_big_endian_or_signed8bit,
                   char *src_buffer, long src_buf_size, int src_samp_byte,
                   spBool src_big_endian_or_signed8bit, int mult2432)
{
    long copy_size;

    if (dest_samp_byte == src_samp_byte
        && (dest_big_endian_or_signed8bit == src_big_endian_or_signed8bit
            || dest_samp_byte >= 2)) {
        copy_size = MIN(dest_buf_size, src_buf_size);
    
        memcpy(dest_buffer, src_buffer, copy_size);
        if (dest_big_endian_or_signed8bit != src_big_endian_or_signed8bit) {
            spSwapByte(dest_buffer, copy_size / dest_samp_byte, dest_samp_byte);
        }
    } else {
        int i;
        int num_unit;
        int loop_count;
        int byte_diff;
        int src_samp_byte2;
        int dest_samp_byte2;
        long k;
        long length;
        char value;
        char buf[16];
        char *ptr;
        char *destp;
        char *srcp;
        unsigned char ucvalue;
        short svalue;
        spLong32 lvalue;
        spBool src_big_endian, src_signed8bit;
        spBool dest_big_endian, dest_signed8bit;

        length = MIN(dest_buf_size / dest_samp_byte, src_buf_size / src_samp_byte);
        destp = dest_buffer;
        srcp = src_buffer;

#if 0
        printf("original src: samp_byte = %d, big_endian = %d, original dest: samp_byte = %d, big_endian = %d\n",
               src_samp_byte, src_big_endian_or_signed8bit, dest_samp_byte, dest_big_endian_or_signed8bit);
#endif
        
        if (src_samp_byte == 1) {
            src_signed8bit = src_big_endian_or_signed8bit;
            src_big_endian = BYTE_ORDER == LITTLE_ENDIAN ? SP_FALSE : SP_TRUE;
            src_samp_byte2 = src_signed8bit ? 1 : 2;
        } else {
            src_big_endian = src_big_endian_or_signed8bit;
            src_signed8bit = SP_FALSE;
            src_samp_byte2 = src_samp_byte;
        }
        if (dest_samp_byte == 1) {
            dest_signed8bit = dest_big_endian_or_signed8bit;
            dest_big_endian = BYTE_ORDER == LITTLE_ENDIAN ? SP_FALSE : SP_TRUE;
            dest_samp_byte2 = dest_signed8bit ? 1 : 2;
        } else {
            dest_big_endian = dest_big_endian_or_signed8bit;
            dest_signed8bit = SP_FALSE;
            dest_samp_byte2 = dest_samp_byte;
        }
#if 0
        printf("src: samp_byte2 = %d (%d), big_endian = %d, dest: samp_byte2 = %d (%d), big_endian = %d\n",
               src_samp_byte2, src_samp_byte, src_big_endian, dest_samp_byte2, dest_samp_byte, dest_big_endian);
#endif
        
        byte_diff = dest_samp_byte2 - src_samp_byte2;
        num_unit = src_samp_byte2 - 1;
        loop_count = src_samp_byte2 / 2;
        copy_size = 0;

        for (k = 0; k < length; k++) {
            memset(buf, 0, dest_samp_byte2);
            if (src_samp_byte == 1 && src_signed8bit == SP_FALSE) {
                memcpy(&ucvalue, srcp, 1);
                svalue = 256 * ((short)ucvalue - 128);
                memcpy(buf, &svalue, src_samp_byte2);
            } else {
                memcpy(buf, srcp, src_samp_byte);
            }
            if (mult2432 == 1 && src_samp_byte2 == 4) {
                if (
#if BYTE_ORDER == LITTLE_ENDIAN
                    src_big_endian == SP_FALSE
#else
                    src_big_endian == SP_TRUE
#endif
                    ) {
                    memcpy(&lvalue, buf, src_samp_byte2);
                    lvalue *= 256;
                    memcpy(buf, &lvalue, src_samp_byte2);
                }
            }
            if (dest_big_endian != src_big_endian) {
                for (i = 0; i < loop_count; i++) {
                    value = buf[i];
                    buf[i] = buf[num_unit - i];
                    buf[num_unit - i] = value;
                }
            }
            if (mult2432 == 1 && src_samp_byte2 == 4) {
                if (
#if BYTE_ORDER == LITTLE_ENDIAN
                    src_big_endian == SP_TRUE
#else
                    src_big_endian == SP_FALSE
#endif
                    ) {
                    memcpy(&lvalue, buf, src_samp_byte2);
                    lvalue *= 256;
                    memcpy(buf, &lvalue, src_samp_byte2);
                }
            }

            if (dest_samp_byte == 1 && dest_signed8bit == SP_FALSE) {
                ptr = (char *)&svalue;
            } else {
                ptr = destp;
            }
            
            if (dest_samp_byte2 > src_samp_byte2) {
                memset(ptr, 0, dest_samp_byte2);
                if (dest_big_endian) {
                    memcpy(ptr, buf, src_samp_byte2);
                } else {
                    memcpy(ptr + byte_diff, buf, src_samp_byte2);
                }
            } else {
                if (dest_big_endian) {
                    memcpy(ptr, buf, dest_samp_byte2);
                } else {
                    memcpy(ptr, buf - byte_diff, dest_samp_byte2);
                }
            }

            if (dest_samp_byte == 1 && dest_signed8bit == SP_FALSE) {
                ucvalue = (unsigned char)(svalue / 256 + 128);
                memcpy(destp, &ucvalue, 1);
            }

            copy_size += dest_samp_byte;
            destp += dest_samp_byte;
            srcp += src_samp_byte;
        }
    }
    
    return copy_size;
}
