#include <Python.h>

#include <sp/spBase.h>
#include <sp/spThread.h>
#include <sp/spAudioP.h>
#include "spaudio_c.h"

static spBool spAudioCallbackFuncForPython(spAudio audio, spAudioCallbackType call_type,
                                           void *data1, void *data2, void *user_data)
{
    PyObject *obj;
    PyObject *func;
    PyObject *audiopy;
    PyObject *args;
    PyObject *typeobj;
    PyObject *cbdata;
    PyObject *result;
    PyGILState_STATE gstate;
    long ret;

    spDebug(100, "spAudioCallbackFuncForPython", "thread_id = %ld\n", (long)spGetCurrentThreadId());
    
    if (!(call_type == SP_AUDIO_OUTPUT_POSITION_CALLBACK
          || call_type == SP_AUDIO_OUTPUT_BUFFER_CALLBACK)) {
        return SP_FALSE;
    }
        
    spDebug(100, "spAudioCallbackFuncForPython", "call_type = %lx\n", call_type);
    
    obj = (PyObject *)user_data;

    if (PyArg_ParseTuple(obj, "OOO", &func, &audiopy, &args)) {
        if (!PyCallable_Check(func)) {
            return SP_FALSE;
        }

        ret = 0;

        typeobj = PyLong_FromUnsignedLong(call_type);

        if (call_type == SP_AUDIO_OUTPUT_POSITION_CALLBACK) {
            spLong *position = (spLong *)data1;
            spDebug(100, "spAudioCallbackFuncForPython", "SP_AUDIO_OUTPUT_POSITION_CALLBACK: position = %ld\n", (long)*position);
            cbdata = PyLong_FromLong((long)*position);
        } else {
            char *buffer = (char *)data1;
            long *buf_size = (long *)data2;
            spDebug(100, "spAudioCallbackFuncForPython", "SP_AUDIO_OUTPUT_BUFFER_CALLBACK: buf_size = %ld\n", (long)*buf_size);
            /*cbdata = PyByteArray_FromStringAndSize(buffer, (int)*buf_size);*/
            cbdata = PyBytes_FromStringAndSize(buffer, (int)*buf_size);
        }

        gstate = PyGILState_Ensure();
        result = PyObject_CallFunctionObjArgs(func, audiopy, typeobj, cbdata, args, NULL);
        PyGILState_Release(gstate);
        
        if (result != NULL) {
            ret = PyLong_AsLong(result);
            Py_DECREF(result);
            spDebug(100, "spAudioCallbackFuncForPython", "PyObject_CallFunctionObjArgs ret = %ld\n", ret);
        } else {
            spDebug(100, "spAudioCallbackFuncForPython", "PyObject_CallFunctionObjArgs failed\n");
        }

            
        Py_DECREF(typeobj);
        Py_DECREF(cbdata);
        
        return ret ? SP_TRUE : SP_FALSE;
    }

    return SP_FALSE;
}

int spSetAudioCallbackFunc_(spAudio audio, spAudioCallbackType call_type, PyObject *obj)
{
    PyEval_InitThreads();
    
    if (audio->call_data != NULL) {
        Py_DECREF((PyObject *)audio->call_data);
    }
    Py_XINCREF(obj);
    spSetAudioCallbackFunc(audio, call_type, spAudioCallbackFuncForPython, obj);

    return 1;
}

long spReadAudioBuffer_(spAudio audio, char *buffer, long buf_size, long offset_byte, long length_byte)
{
    if (length_byte <= 0) {
        length_byte = buf_size - offset_byte;
    } else {
        length_byte = MIN(length_byte, buf_size - offset_byte);
    }

    return spReadAudioBuffer(audio, buffer + offset_byte, length_byte);
}

long spWriteAudioBuffer_(spAudio audio, char *buffer, long buf_size, long offset_byte, long length_byte)
{
    if (length_byte <= 0) {
        length_byte = buf_size - offset_byte;
    } else {
        length_byte = MIN(length_byte, buf_size - offset_byte);
    }

    return spWriteAudioBuffer(audio, buffer + offset_byte, length_byte);
}

long spReadAudioDoubleBufferWeighted_(spAudio audio, char *buffer, long buf_size, double weight,
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
    
    return spReadAudioDoubleWeighted(audio, (double *)(buffer + offset_byte), length, weight);
}

long spWriteAudioDoubleBufferWeighted_(spAudio audio, char *buffer, long buf_size, double weight,
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
    
    return spWriteAudioDoubleWeighted(audio, (double *)(buffer + offset_byte), length, weight);
}
