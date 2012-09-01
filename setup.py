#!/usr/bin/env python
# -----------------------------------------------------------------------------
#    Vakhshour - Event and Message layer application
#    Copyright (C) 2012 Yellowen
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
# -----------------------------------------------------------------------------

from distutils.core import setup

setup(name='Vakhshour',
      version='0.91.45',
      description='Event and Message layer application',
      author='Sameer Rahmani',
      author_email='lxsameer@gnu.org',
      url='http://vakhshour.yellowen.com/',
      download_url="http://vakhshour.yellowen.com/downloads/",
      keywords=('Event', 'message', 'transport'),
      license='GPL v2',
      scripts=["vakhshourd"],
      data_files=[("/etc/vakhshour/", ["conf/vakhshour.json"]), ],
      packages=['vakhshour', 'vakhshour.events', 'vakhshour.amp'],
      requires=['twisted', 'pyopenssl', 'pycrypto'],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities',
          ]
)
