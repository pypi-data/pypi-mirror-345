Introduction
============

This package is the Python version of `spAudio library <http://www-ie.meijo-u.ac.jp/labs/rj001/spLibs/index.html>`_ 
providing :doc:`spaudio</spaudio>` module which enables fullduplex audio device I/O and
:doc:`spplugin</spplugin>` module which enables plugin-based file I/O
supporting many sound formats including WAV, AIFF, MP3, Ogg Vorbis, FLAC, ALAC, raw, and more.


Installation
------------

You can use ``pip`` command to install the binary package::
  
  pip install spaudio

If you use `Anaconda <https://www.anaconda.com/distribution/>`_
or `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_ ,
``conda`` command with "bannohideki" channel can be used::

  conda install -c bannohideki spaudio
  
Note that this package doesn't support Python 2.

The linux version also requires `spPlugin <http://www-ie.meijo-u.ac.jp/labs/rj001/spLibs/index.html>`_
installation (audio device I/O requires the pulsesimple plugin 
based on `PulseAudio <https://www.freedesktop.org/wiki/Software/PulseAudio/>`_ ).
You can install it by using ``dpkg`` (Ubuntu) or ``rpm`` (CentOS) command with one of the following
packages.

* Ubuntu 18
  
  * amd64: http://www-ie.meijo-u.ac.jp/labs/rj001/archive/deb/ubuntu18/spplugin_0.8.5-5_amd64.deb
  * i386: http://www-ie.meijo-u.ac.jp/labs/rj001/archive/deb/ubuntu18/spplugin_0.8.5-5_i386.deb
    
* Ubuntu 16

  * amd64: http://www-ie.meijo-u.ac.jp/labs/rj001/archive/deb/ubuntu16/spplugin_0.8.5-5_amd64.deb
  * i386: http://www-ie.meijo-u.ac.jp/labs/rj001/archive/deb/ubuntu16/spplugin_0.8.5-5_i386.deb
  
* Ubuntu 14

  * amd64: http://www-ie.meijo-u.ac.jp/labs/rj001/archive/deb/ubuntu14/spplugin_0.8.5-5_amd64.deb
  * i386: http://www-ie.meijo-u.ac.jp/labs/rj001/archive/deb/ubuntu14/spplugin_0.8.5-5_i386.deb

* CentOS 7

  * http://www-ie.meijo-u.ac.jp/labs/rj001/archive/rpm/el7/x86_64/spPlugin-0.8.5-5.x86_64.rpm

* CentOS 6

  * http://www-ie.meijo-u.ac.jp/labs/rj001/archive/rpm/el6/x86_64/spPlugin-0.8.5-5.x86_64.rpm

If you want to use ``apt`` (Ubuntu) or ``yum`` (CentOS),
see `this page (for Ubuntu) <http://www-ie.meijo-u.ac.jp/labs/rj001/spLibs/linux_download.html#apt_dpkg>`_
or `this page (for CentOS) <http://www-ie.meijo-u.ac.jp/labs/rj001/spLibs/linux_download.html#yum>`_ .


Change Log
----------

- Version 0.7.15

  * Added spaudio.open function to spaudio module.
  * Added support for open call of spaudio module with keyword arguments.

- Version 0.7.14

  * Added :doc:`spplugin</spplugin>` module which enables plugin-based audio file I/O.

- Version 0.7.13

  * Initial public release.


Build
-----
To build this package, the following are required.

* `SWIG <http://www.swig.org/>`_
* `spBase and spAudio <http://www-ie.meijo-u.ac.jp/labs/rj001/spLibs/index.html>`_


Official Site
-------------
The official web site is: http://www-ie.meijo-u.ac.jp/labs/rj001/spLibs/python/spAudio/en/index.html

Japanese web site is also available: http://www-ie.meijo-u.ac.jp/labs/rj001/spLibs/python/spAudio/ja/index.html
