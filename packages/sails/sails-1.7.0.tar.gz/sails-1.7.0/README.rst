Spectral Analysis In Linear Systems
===================================

This repository contains the Spectral Analysis In Linear Systems tools
for python (sails)

Installation
============

If you just want to install sails to use it, the easiest way is to get it from pip
using ```pip install sails```.

If you are reading this file, you probably have a source distribution of sails and
may be interested in working on the software.  In that case, as there is no
compiled code, you can simply set your ```PYTHONPATH``` to include this directory.
Alternatively, you can use ```python3 setup.py build``` or run ```make``` or
```make doc``` to install the software into the normal ```build/``` directory
and/or build the documentation using sphinx.

Documentation
=============

Documentation for the current release can be found at https://sails.readthedocs.org

Dependencies
============

See the requirements.txt file.

Some of these aren't strict dependencies, but are instead what we develop
against (i.e. we don't guarantee not to use features which only exist from that
release onwards).

Repository
==========

The main git repository can be found at https://gitlab.com/sails-dev/analysis/sails

Contributing
============

If you wish to raise issues on, or contribute patches to SAILS, you will need
an account on gitlab.com.  If you wish to be able to create MRs please tag
@ajquinn or @mhy in the relevant issue and we will give you permission to do
so.  Alternatively, please feel free to email one of us.

Authors
=======

Andrew Quinn <andrew.quinn@psych.ox.ac.uk>
Mark Hymers <mark.hymers@ynic.york.ac.uk>

License
=======

This project is currently licensed under the GNU General Public Licence 2.0 or
higher.  For the avoidance of doubt, the authors intend that if the code is
imported into a project which is not licensed under a GPL 2.0 compatible
license, an alternative license arranged must be acquired.  For alternative
license arrangements such as use in commercial products for which you do not
which to release the source code under a GPL compatible license, please contact
the authors.  The authors are also available for consultancy regarding this
toolbox and associated methods.
