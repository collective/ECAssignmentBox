Overview
========

ECAssignmentBox is a Plone product which allows the creation,
submission and grading of online assignments (exercises, homework),
both for traditional on-site courses and for e-learning.

Download
========

`plone.org products page`_

.. _plone.org products page: http://plone.org/products/ecassignmentbox/

Prerequisites
=============

To use ECAssignmentBox you need a current Plone installation, 
specifically Plone 4.x.  Check `plone.org`_ for Plone's 
prerequisites.

.. _plone.org: http://plone.org/products/plone

Installation
============

See the `Installing an Add-on Product`_ tutorial for more detailed 
product installation instructions.
        
.. _Installing an Add-on Product: http://plone.org/documentation/tutorial/third-party-products/installing

Installing with buildout
------------------------

If you are using `buildout`_ to manage your instance installing 
ECAssignmentBox is very simple.  You can install it by adding it to the 
eggs line for your instance::

  [instance]
  eggs =
      ... 
      Products.ECAssignmentBox

After updating the configuration you need to run ``bin/buildout``, 
which will take care of updating your system.

Then restart your zope instance and use the Add/Remove products page
in Site Setup to install ECAssignmentBox.

.. _buildout: http://pypi.python.org/pypi/zc.buildout

Installing without buildout
---------------------------

Move (or symlink) the ``ECAssignmentBox`` folder of this project
(``Products.ECAssignmentBox/Products/ECAssignmentBox``) into the 
``Products`` directory of the Zope instance it has to be installed 
for, and restart the server.  Use the Add/Remove products page in 
Site Setup to install ECAssignmentBox.

Support
=======

For questions and discussions about ECAssignmentBox, please join the
`eduComponents mailing list`_.

.. _eduComponents mailing list: https://listserv.uni-magdeburg.de/mailman/listinfo/educomponents

Credits
=======

ECAssignmentBox was written by `Mario Amelung`_ and 
`Michael Piotrowski`_.

Additional programming by Marcel Abou Khalil and Sascha Peilicke.

ECAssignmentBox was inspired by `LTAssignmentBox`_.  The products 
don't share any code, though.

The Statistics class was written by `Chad J. Schroeder`_.  It is 
licensed under the `Python license`_.

The icons used in ECAssignmentBox are from the `Silk icon set`_ by 
Mark James.  They are licensed under a `Creative Commons Attribution 
2.5 License`_.

ECAssignmentBox was ported to Plone 3 and 4 by `Eudemonia Solutions AG`_ 
with support from `Katrin Krieger`_ and the Otto-von-Guericke 
University of Magdeburg.

.. _Mario Amelung: mario.amelung@gmx.de
.. _Michael Piotrowski: mxp@dynalabs.de
.. _LTAssignmentBox: http://lawtec.net/projects/ltassignmentbox
.. _Chad J. Schroeder: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/409413
.. _Python license: http://www.python.org/license
.. _Silk icon set: http://www.famfamfam.com/lab/icons/silk/
.. _Creative Commons Attribution 2.5 License: http://creativecommons.org/licenses/by/2.5/
.. _Eudemonia Solutions AG: http://www.eudemonia-solutions.de/
.. _Katrin Krieger: http://wdok.cs.uni-magdeburg.de/Members/kkrieger/
