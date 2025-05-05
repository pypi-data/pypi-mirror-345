#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import platform
from setuptools import setup
from setuptools import Extension

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE.txt') as f:
    license = f.read()

is_64bits = sys.maxsize > 2**32

sptop = '../..'
ccopts = []
# ccdefs = [('SWIGRUNTIME_DEBUG', 1)]
ccdefs = []
ldopts = []
libpath = sptop + '/lib'
ext_include_dirs = [sptop + '/spAudio', sptop + '/spBase', sptop + '/include']

all_packages = ['_spaudio', '_spplugin']
sysdirname = ''

if sys.platform == 'win32':
    # ldopts = ['/DEBUG', '/OPT:REF', '/OPT:ICF']
    # ccopts = ['/Zi']
    ext_libraries = ['spAudio', 'spBase', 'winmm',
                     'shell32', 'User32', 'Kernel32']

    py_version_num = sys.version_info[0]*10 + sys.version_info[1]

    if is_64bits:
        # libpath = sptop + '/lib/x64/v141'
        if py_version_num <= 36:
            libpath = sptop + '/lib/x64/v140'
        else:
            # libpath = sptop + '/lib/x64/v140'
            libpath = sptop + '/lib/x64/v141'
        sysdirname = 'win64'
    else:
        # libpath = sptop + '/lib/v141'
        if py_version_num <= 36:
            # libpath = sptop + '/lib/v140_xp'
            libpath = sptop + '/lib/v140'
        else:
            # libpath = sptop + '/lib/v140_xp'
            # libpath = sptop + '/lib/v140'
            libpath = sptop + '/lib/v141'
        sysdirname = 'win32'
    pluginfiles_list = ['*.dll']
elif sys.platform == 'darwin':
    import subprocess
    sdktop = subprocess.getoutput('xcrun --sdk macosx --show-sdk-path')
    ldopts = ['--sysroot=' + sdktop, '-Wl,-framework,AudioToolbox',
              '-Wl,-framework,AudioUnit', '-Wl,-framework,CoreAudio']
    if platform.machine() == 'arm64':
        ext_libraries = ['spa.mac64ub', 'spb.mac64ub']
        sysdirname = 'mac64'
    else:
        ext_libraries = ['spa.mac64', 'spb.mac64']
        sysdirname = 'mac64'

    pluginfiles_list = ['*.bundle/Contents/Info.plist', '*.bundle/Contents/MacOS/*',
                        '*.bundle/Contents/Resources/English.lproj/InfoPlist.strings']
else:
    if is_64bits:
        ext_libraries = ['spa.linux64', 'spb.linux64']
    else:
        ext_libraries = ['spa.linux-glibc', 'spb.linux-glibc']

if sysdirname:
    all_packages.append('_spplugins')
    all_package_data = {'_spplugins': [os.path.join(sysdirname, s) for s in pluginfiles_list]}
else:
    all_package_data = {}

if not os.path.isfile('_spaudio/spaudio_c_wrap.c') \
   or not os.path.isfile('_spaudio/spaudio_c.py'):
    ext_sources = ['_spaudio/spaudio_c.i', '_spaudio/spaudio_c.c']
else:
    ext_sources = ['_spaudio/spaudio_c_wrap.c', '_spaudio/spaudio_c.c']

ext_spaudio = Extension(
    '_spaudio._spaudio_c',
    ext_sources,
    swig_opts=['-threads', '-modern', '-I' + sptop + '/spAudio',
               '-I' + sptop + '/spBase', '-I' + sptop + '/include'],
    include_dirs=ext_include_dirs,
    define_macros=ccdefs,
    extra_compile_args=ccopts,
    extra_link_args=ldopts,
    libraries=ext_libraries,
    library_dirs=[libpath]
)

if not os.path.isfile('_spplugin/spplugin_c_wrap.c') \
   or not os.path.isfile('_spplugin/spplugin_c.py'):
    ext_sources_spplugin = ['_spplugin/spplugin_c.i', '_spplugin/spplugin_c.c']
else:
    ext_sources_spplugin = ['_spplugin/spplugin_c_wrap.c', '_spplugin/spplugin_c.c']

ext_spplugin = Extension(
    '_spplugin._spplugin_c',
    ext_sources_spplugin,
    swig_opts=['-threads', '-modern', '-I' + sptop + '/spAudio',
               '-I' + sptop + '/spBase', '-I' + sptop + '/include'],
    include_dirs=ext_include_dirs,
    define_macros=ccdefs,
    extra_compile_args=ccopts,
    extra_link_args=ldopts,
    libraries=ext_libraries,
    library_dirs=[libpath]
)

setup(
    name='spaudio',
    version='0.7.18',
    description='spAudio audio I/O library',
    long_description=readme,
    long_description_content_type='text/x-rst',
    url='https://www-ie.meijo-u.ac.jp/labs/rj001/spLibs/python/spAudio/en/index.html',
    keywords=['audio', 'sound', 'play', 'record', 'I/O', 'file',
              'capture', 'wav', 'aiff', 'caf', 'ogg', 'mp3',
              'flac', 'alac', 'python', 'library'],
    ext_modules=[ext_spaudio, ext_spplugin],
    py_modules=['spaudio', 'spplugin'],
    packages=all_packages,
    package_data=all_package_data,
    install_requires=[''],
    extras_require={'numpy': ['numpy']},
    author='Hideki Banno',
    author_email='banno@meijo-u.ac.jp',
    license='MIT',
    platforms=['posix', 'nt'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Sound/Audio :: Analysis',
        'Topic :: Multimedia :: Sound/Audio :: Capture/Recording',
        'Topic :: Multimedia :: Sound/Audio :: Conversion',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
