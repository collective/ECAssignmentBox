# -*- coding: utf-8 -*-
#
# $Id: setup.py 1237 2009-09-23 20:13:15Z amelung $

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = read('Products', 'ECAssignmentBox', 'version.txt').strip()
readme  = read('Products', 'ECAssignmentBox', 'README.txt')
history = read('Products', 'ECAssignmentBox', 'CHANGES.txt')

long_description = readme + '\n\n' + history

setup(name='Products.ECAssignmentBox',
      version=version,
      description = "Creation, submission and grading of online assignments (exercises, homework).",
      long_description = long_description,

      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords = '',
      author = 'Mario Amelung and Michael Piotrowski',
      author_email = 'mario.amelung@gmx.de and mxp@dynalabs.de',
      url = 'http://plone.org/products/ecassignmentbox/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
