Id Image Store
==============

Installation
------------

Dependencies:

* Python 2.4

* Python 2.4 compilation environment (including C compiler)

* pygame (optional)

To install::

  $ cd store

  $ python2.4 bootstrap.py
  
  $ bin/buildout

After this, the various scripts exist in the 'bin' directory.

Usage
-----

To start the store backend (on port 8080), run:

  $ bin/zopectl fg

You can access the web UI by browsing to
http://localhost:8080. Username 'admin', password 'admin'.

To create a new instance of the application, use 'Add application' and
name your application 'store' (or any name you wish, but the rest of
the examples below assume 'store').

To view the REST interface in your browser you can then browse to the
application (http://localhost:8080/store).

The filler script can be used to fill the store with data. It uses the REST
interface, so the backend needs to be running first.

If you use::

  $ bin/filler

then you will get a brief usage instruction.

Let's create a new session in the store, and create a group in that
session filling it with the images in a directory::

  $ bin/filler http://localhost:8080/store demo store /path/to/images_dir/

The filler script will now upload the images.

To see the changed state of the backend, you can look at
http://localhost:8080/store again.

To try the demo pygame frontend you need to have pygame installed. You can
then connect to the store with the following command:

  $ bin/frontend http://localhost:8080/store/sessions/demo

More information
----------------

Consult the following documents for technical information:

* src/imagestore/model.txt

* src/imagestore/rest.txt

* src/imagestore/search.txt

* src/imagestore/fake.txt

* src/imagestore/comprehensive.txt

There is also a website:

http://studiolab.io.tudelft.nl/imageSTORE/

License
-------

imageSTORE - a web service for the storing and organization of images

Copyright (C) 2007-2008, ID Studio Lab and Startifact

This library is free software; you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation; either version 2.1 of the
License, or (at your option) any later version.

This library is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301 USA
