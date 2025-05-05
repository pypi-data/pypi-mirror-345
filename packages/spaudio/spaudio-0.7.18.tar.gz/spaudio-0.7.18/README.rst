Introduction
============

This package is the Python version of `spAudio library <https://www-ie.meijo-u.ac.jp/labs/rj001/spLibs/index.html>`_ 
providing `spaudio module <https://www-ie.meijo-u.ac.jp/labs/rj001/spLibs/python/spAudio/en/spaudio.html>`_ 
which enables fullduplex audio device I/O and
`spplugin module <https://www-ie.meijo-u.ac.jp/labs/rj001/spLibs/python/spAudio/en/spplugin.html>`_ 
which enables plugin-based file I/O supporting many sound formats
including WAV, AIFF, MP3, Ogg Vorbis, FLAC, ALAC, raw, and more.
The spplugin module also supports 24/32-bit sample size used in high-resolution audio files, so
you can easily load data with 24/32-bit sample size into `NumPy <http://www.numpy.org/>`_'s ndarray.


Installation
============

You can use ``pip`` command to install the binary package::
  
  pip install spaudio

If you use `Anaconda <https://www.anaconda.com/distribution/>`_
or `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_ ,
``conda`` command with "bannohideki" channel can be used::

  conda install -c bannohideki spaudio
  
`NumPy <http://www.numpy.org/>`_ package is needed only if you want to
use NumPy arrays. If you don't use NumPy arrays, no external package is required.
Note that this package doesn't support Python 2.

The linux version also requires `spPlugin <https://www-ie.meijo-u.ac.jp/labs/rj001/spLibs/index.html>`_
installation (audio device I/O requires the pulsesimple plugin 
based on `PulseAudio <https://www.freedesktop.org/wiki/Software/PulseAudio/>`_ ).
You can install it by using ``dpkg`` (Ubuntu) or ``rpm`` (RHEL) command with one of the following
packages. The files for RHEL were tested on CentOS 7 (RHEL 7) and AlmaLinux 8/9 (RHEL 8/9).

* Ubuntu 24
  
  * amd64: https://www-ie.meijo-u.ac.jp/labs/rj001/archive/deb/ubuntu24/spplugin_0.8.6-4_amd64.deb
    
* Ubuntu 22
  
  * amd64: https://www-ie.meijo-u.ac.jp/labs/rj001/archive/deb/ubuntu22/spplugin_0.8.6-4_amd64.deb
    
* Ubuntu 20
  
  * amd64: https://www-ie.meijo-u.ac.jp/labs/rj001/archive/deb/ubuntu20/spplugin_0.8.6-4_amd64.deb
    
* Ubuntu 18
  
  * amd64: https://www-ie.meijo-u.ac.jp/labs/rj001/archive/deb/ubuntu18/spplugin_0.8.6-4_amd64.deb
  * i386: https://www-ie.meijo-u.ac.jp/labs/rj001/archive/deb/ubuntu18/spplugin_0.8.6-4_i386.deb
    
* Ubuntu 16

  * amd64: https://www-ie.meijo-u.ac.jp/labs/rj001/archive/deb/ubuntu16/spplugin_0.8.6-4_amd64.deb
  * i386: https://www-ie.meijo-u.ac.jp/labs/rj001/archive/deb/ubuntu16/spplugin_0.8.6-4_i386.deb
  
* RHEL 9
  
  * https://www-ie.meijo-u.ac.jp/labs/rj001/archive/rpm/el9/x86_64/spPlugin-0.8.6-4.x86_64.rpm

* RHEL 8

  * https://www-ie.meijo-u.ac.jp/labs/rj001/archive/rpm/el8/x86_64/spPlugin-0.8.6-4.x86_64.rpm

* RHEL 7

  * https://www-ie.meijo-u.ac.jp/labs/rj001/archive/rpm/el7/x86_64/spPlugin-0.8.6-4.x86_64.rpm

If you want to use ``apt`` (Ubuntu) or ``yum/dnf`` (RHEL),
see `this page (for Ubuntu) <https://www-ie.meijo-u.ac.jp/labs/rj001/spLibs/linux_download.html#apt_dpkg>`_
or `this page (for RHEL) <https://www-ie.meijo-u.ac.jp/labs/rj001/spLibs/linux_download.html#yum>`_ .


Change Log
==========

- Version 0.7.18
  
  * Rebuilt binaries.
  * Added support for Python 3.13.

- Version 0.7.17

  * Rebuilt binaries.
  * Updated documents.
  * Fixed some bugs of plugins for spplugin module.
  
- Version 0.7.16

  * Added high-level functions of audioread and audiowrite to spplugin module.
  * Added functions of readframes/readrawframes and writeframes/writerawframes
    to spaudio module and spplugin module.
  * Changed some specification of spplugin.

- Version 0.7.15

  * Added spaudio.open function to spaudio module.
  * Added support for open call of spaudio module with keyword arguments.

- Version 0.7.14

  * Added spplugin module which enables plugin-based audio file I/O.

- Version 0.7.13

  * Initial public release.


Build
=====
To build this package, the following are required.

* `SWIG <http://www.swig.org/>`_
* `spBase and spAudio <https://www-ie.meijo-u.ac.jp/labs/rj001/spLibs/index.html>`_


Official Site
=============
The official web site is: https://www-ie.meijo-u.ac.jp/labs/rj001/spLibs/python/spAudio/en/index.html

Japanese web site is also available: https://www-ie.meijo-u.ac.jp/labs/rj001/spLibs/python/spAudio/ja/index.html
