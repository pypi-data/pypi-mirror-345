#include <Python.h>
#include <stdarg.h>
#include <stdio.h>
#include <png.h>
#include "gbagfx/lz.h"

#if defined(__CLING__) /* hide gbagfx definitions in cppyy */
namespace _gbagfx {
#define WITH_ASSERT
#endif

#if defined(__GNUC__)
#define unlikely(expr) __builtin_expect(!!(expr), 0)
#else
#define unlikely(expr) (!!(expr))
#endif


/* NOTE: overwriting printf makes it impossible to run multiple mains
         concurrently without loading the module multiple times,
         but luckily it's fast. */
static PyObject *logger = NULL;
static PyObject *semaphore = NULL;
static char *stdoutbuf = NULL;
#define STDOUT_LOGGER_LEVEL "debug"
#define STDERR_LOGGER_LEVEL "error"

static int gbagfx_fprintf(FILE *f, const char *fmt, ...)
{
    int res;
    char buf[1024];
    char *heap = NULL;
    va_list args;
    va_start(args, fmt);
    if (logger && (f == stdout || f == stderr)) {
        const char *level = (f==stdout) ? STDOUT_LOGGER_LEVEL : STDERR_LOGGER_LEVEL;
        /* try to print to buffer on stack */
        res = vsnprintf(buf, sizeof(buf), fmt, args);
        if (res > 0 && (size_t)res < sizeof(buf)) {
            /* buf valid */
            if (f == stdout) {
                size_t buflen = strlen(buf);
                size_t oldlen = stdoutbuf ? strlen(stdoutbuf) : 0;
                if (!oldlen && buf[buflen-1] == '\n') {
                    /* immediately print stdout if buf is empty and chunk ends in \n. optimized most-common case */
                    buf[buflen-1] = 0;
                    Py_XDECREF(PyObject_CallMethod(logger, level, "(s)", buf));
                } else {
                    /* append to stdoutbuf, see below for printing it */
                    stdoutbuf = (char*)realloc(stdoutbuf, buflen + oldlen + 1);
                    if (!stdoutbuf) {
                        res = -1;
                        goto cleanup;
                    }
                    memcpy(stdoutbuf+oldlen, buf, buflen+1);
                }
            } else {
                /* immediately print stderr chunk */
                Py_XDECREF(PyObject_CallMethod(logger, level, "(s)", buf));
            }
        } else if (res > 0) {
            /* allocate bigger buffer on heap */
            heap = (char*)malloc((size_t)res+1);
            if (heap) {
                va_end(args);
                va_start(args, fmt);
                res = vsnprintf(heap, (size_t)res+1, fmt, args);
                if (res > 0) {
                    /* heap valid */
                    if (f == stdout) {
                        if (!stdoutbuf) {
                            /* replace stdoutbuf by new chunk, see below for printing it */
                            stdoutbuf = heap;
                            heap = NULL;
                        } else {
                            /* append new chunk to stdoutbuf, see below for printing it */
                            size_t oldlen = strlen(stdoutbuf);
                            size_t heaplen = strlen(heap);
                            stdoutbuf = (char*)realloc(stdoutbuf, oldlen + heaplen + 1);
                            if (!stdoutbuf) {
                                res = -1;
                                goto cleanup;
                            }
                            memcpy(stdoutbuf + oldlen, heap, heaplen + 1);
                        }
                    } else {
                        /* immediately print stderr chunk */
                        Py_XDECREF(PyObject_CallMethod(logger, level, "(s)", heap));
                    }
                }
            }
        }
        if (f == stdout && stdoutbuf && *stdoutbuf) {
            /* print stdoutbuf if it ends in newline */
            size_t newlen = strlen(stdoutbuf);
            if (stdoutbuf[newlen-1] == '\n') {
                stdoutbuf[newlen-1] = 0;
                Py_XDECREF(PyObject_CallMethod(logger, level, "(s)", stdoutbuf));
                free(stdoutbuf);
                stdoutbuf = NULL;
            }
        }
    }
    else {
        res = vfprintf(f, fmt, args);
    }
cleanup:
    free(heap);
    va_end(args);
    if (PyErr_Occurred()) PyErr_Clear(); /* ignore errors for bad printf */
    return res;
}


#define NO_UI
#define WITH_MULTIWORLD /* force on for wasm support */
#define exit(N) return N
#define die(...) do { fprintf(stderr, __VA_ARGS__); return 1; } while (0)
#define main gbagfx_main
#define printf(...) fprintf(stdout, __VA_ARGS__)
#define fprintf gbagfx_fprintf
#include "gbagfx/main.c"
#undef printf
#undef fprintf
#undef main

#if defined(__CLING__) /* see above */
}
using namespace _gbagfx;
#endif

/* helpers */
static int
path2ansi(PyObject *stringOrPath, void* result)
{
    /* NOTE: PyUnicode_FSConverter does not work anymore on windows for fopen()
             see https://www.python.org/dev/peps/pep-0529/ */
    PyObject **out = (PyObject **) result;
    assert(stringOrPath); /* TODO: raise exception */
    assert(out); /* TODO: raise exception */
    if (Py_TYPE(stringOrPath) == &PyBytes_Type) {
        /* already bytes, assume ansi */
        *out = stringOrPath;
        Py_INCREF(stringOrPath);
    }
    else if (PyObject_HasAttrString(stringOrPath, "__fspath__")) {
        /* path */
        PyObject *str, *fspath;
        fspath = PyObject_GetAttrString(stringOrPath, "__fspath__");
        if (!fspath) return 0;
        str = PyObject_CallObject(fspath, NULL); /* to string */
        Py_DECREF(fspath);
        if (!str) return 0;
        *out = PyUnicode_EncodeLocale(str, "strict"); /* to ansi */
        Py_DECREF(str);
    } else {
        /* already string */
        *out = PyUnicode_EncodeLocale(stringOrPath, "strict"); /* to ansi */
    }
    if (!*out) return 0;
    return 1;
}

/* methods */
static PyObject *_gbagfx_main(PyObject *self, PyObject *py_args) {
    /* _gbagfx.main call signature:
        input_path: Path, output_path: Path
    */

    /* original main signature:
          int argc, char** argv: { gbagfx INPUT_PATH OUTPUT_PATH [options...] }
    */

    PyObject *pyres = NULL;
    PyObject *oinput, *ooutput;
    const char *input;
    const char *output;
    PyObject *logging;

    if (!PyArg_ParseTuple(py_args, "O&O&", path2ansi, &oinput, path2ansi, &ooutput)) {
        goto error;
    }

    input = PyBytes_AS_STRING(oinput);
    output = PyBytes_AS_STRING(ooutput);

    /* if multithreading is enabled, wait for the previous thread to finish
       before touching any globals */
    if (semaphore) {
        PyObject *lock = PyObject_CallMethod(semaphore, "acquire", NULL);
        if (!lock) goto cleanup; // exception
        Py_DECREF(lock);
    }

    /* setup printf redirection */
    assert(!logger);
    logging = PyImport_AddModule("logging");
    if (!logging) goto release_lock;
    logger = PyObject_CallMethod(logging, "getLogger", "(s)", "Pokemon Emerald");
    if (!logger) goto release_lock;

    do {
        int argc = 3;
        char *argv[3] = {
            "main", input, output
        };

        int res = gbagfx_main(argc, argv);
        pyres = PyLong_FromLong(res);
    } while (false);

    /* flush and free stdout redirection buffer */
    if (!PyErr_Occurred() && stdoutbuf && *stdoutbuf) {
        Py_XDECREF(PyObject_CallMethod(logger, STDOUT_LOGGER_LEVEL, "(s)", stdoutbuf));
        if (PyErr_Occurred()) PyErr_Clear(); // ignore errors for bad printf
    }
    free(stdoutbuf);
    stdoutbuf = NULL;

    /* cleanup */
    Py_DECREF(logger);
    logger = NULL;

release_lock:
    if (semaphore) {
        PyObject *release = PyObject_CallMethod(semaphore, "release", NULL);
        if (!release) {
            Py_DECREF(pyres);
            pyres = NULL; // exception
            goto cleanup;
        }
        Py_DECREF(release);
    }
cleanup:
    Py_DECREF(oinput);
    Py_DECREF(ooutput);
error:
    return pyres;
}

/* methods */
static PyObject *_gbagfx_lz_decompression(PyObject *self, PyObject *py_args) {
    Py_buffer *pyres;
    const char *inputData;
    Py_ssize_t inputDataLength;

    PyObject *logging;

    if (!PyArg_ParseTuple(py_args, "y#", inputData, &inputDataLength)) {
        goto error;
    }

    /* if multithreading is enabled, wait for the previous thread to finish
       before touching any globals */
    if (semaphore) {
        PyObject *lock = PyObject_CallMethod(semaphore, "acquire", NULL);
        if (!lock) goto cleanup; // exception
        Py_DECREF(lock);
    }

    /* setup printf redirection */
    assert(!logger);
    logging = PyImport_AddModule("logging");
    if (!logging) goto release_lock;
    logger = PyObject_CallMethod(logging, "getLogger", "(s)", "Pokemon Emerald");
    if (!logger) goto release_lock;
    
    PyObject *result;

    do {
        int uncompressedSize;
        unsigned char *uncompressedData = LZDecompress((unsigned char *)inputData, (int)inputDataLength, &uncompressedSize);
        result = PyList_New(uncompressedSize);
        for (int i = 1; i < uncompressedSize; i++) {
            PyList_SET_ITEM(result, 0, uncompressedData[i * sizeof(unsigned char)]);
        }
    } while (false);

    /* flush and free stdout redirection buffer */
    if (!PyErr_Occurred() && stdoutbuf && *stdoutbuf) {
        Py_XDECREF(PyObject_CallMethod(logger, STDOUT_LOGGER_LEVEL, "(s)", stdoutbuf));
        if (PyErr_Occurred()) PyErr_Clear(); // ignore errors for bad printf
    }
    free(stdoutbuf);
    stdoutbuf = NULL;

    /* cleanup */
    Py_DECREF(logger);
    logger = NULL;

release_lock:
    if (semaphore) {
        PyObject *release = PyObject_CallMethod(semaphore, "release", NULL);
        if (!release) {
            Py_DECREF(pyres);
            pyres = NULL; // exception
            goto cleanup;
        }
        Py_DECREF(release);
    }
cleanup:
    free(inputData);
error:
    return result;
}

/* module */
static PyMethodDef _gbagfx_methods[] = {
    {"main", _gbagfx_main, METH_VARARGS, "Transform spriter-related data from one type to another."},
    {"decompress_lz", _gbagfx_main, METH_VARARGS, "Transform spriter-related data from one type to another."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef _gbagfx_module = {
    PyModuleDef_HEAD_INIT,
    "_gbagfx", /* name of module */
    NULL,      /* module documentation, may be NULL */
    -1,        /* size of per-interpreter state of the module,
                  or -1 if the module keeps state in global variables. */
    _gbagfx_methods
};

PyMODINIT_FUNC
PyInit__gbagfx(void)
{
    PyObject *m;
    PyObject *threading;

    m = PyModule_Create(&_gbagfx_module);
    if (!m) return NULL;

    // initialize global semaphore. we leak this memory
    threading = PyImport_ImportModule("threading");
    if (threading) {
        semaphore = PyObject_CallMethod(threading, "BoundedSemaphore", NULL);
        Py_DECREF(threading);
        if (!semaphore) goto const_error;
    } else {
        // threading not built in
        PyErr_Clear();
    }

    return m;
const_error:
    Py_XDECREF(m);
    return NULL;
}