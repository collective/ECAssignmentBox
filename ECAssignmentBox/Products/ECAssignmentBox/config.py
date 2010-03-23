# -*- coding: utf-8 -*-
# $Id: config.py 1297 2009-09-27 18:29:20Z amelung $
#
# Copyright (c) 2006-2009 Otto-von-Guericke University Magdeburg
#
# This file is part of ECAssignmentBox.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'
__version__   = '$Revision: 1.2 $'

# Product configuration.
#
# The contents of this module will be imported into __init__.py, the
# workflow configuration and every content type module.
#
# If you wish to perform custom configuration, you may put a file
# AppConfig.py in your product's root directory. The items in there
# will be included (by importing) in this file if found.

from Products.CMFCore.permissions import setDefaultRoles
##code-section config-head #fill in your manual code here
##/code-section config-head

PROJECTNAME = "ECAssignmentBox"

# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner'))
ADD_CONTENT_PERMISSIONS = {
    'ECFolder': 'ECAssignmentBox: Add ECFolder',
    'ECAssignmentBox': 'ECAssignmentBox: Add ECAssignmentBox',
    'ECAssignment': 'ECAssignmentBox: Add ECAssignment',
}

setDefaultRoles('ECAssignmentBox: Add ECFolder', ('Manager','Owner'))
setDefaultRoles('ECAssignmentBox: Add ECAssignmentBox', ('Manager','Owner'))
setDefaultRoles('ECAssignmentBox: Add ECAssignment', ('Manager','Owner'))

product_globals = globals()

# Dependencies of Products to be installed by quick-installer
# override in custom configuration
DEPENDENCIES = []

# Dependend products - not quick-installed - used in testcase
# override in custom configuration
PRODUCT_DEPENDENCIES = []

##code-section config-bottom #fill in your manual code here
##/code-section config-bottom


# Load custom configuration not managed by archgenxml
try:
    from Products.ECAssignmentBox.AppConfig import *
except ImportError:
    pass
