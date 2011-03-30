# -*- coding: utf-8 -*-
# $Id$
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

try: # New CMF 
    from Products.CMFCore import permissions
except: # Old CMF 
    from Products.CMFCore import CMFCorePermissions as permissions


PROJECTNAME = "ECAssignmentBox"
# i18n 
I18N_DOMAIN = 'eduComponents'

product_globals = globals()

# Dependencies of products to be installed by quick-installer
DEPENDENCIES = []

# Dependend products - not quick-installed - used in testcase
PRODUCT_DEPENDENCIES = []

# names and titles
ECA_WORKFLOW_ID = 'ec_assignment_workflow'

# supported mime types for textfields
#EC_MIME_TYPES = ('text/x-web-intelligent',)
EC_MIME_TYPES = ('text/plain', 'text/structured', 'text/x-rst', 'text/x-web-intelligent', 'text/html', )
ECA_MIME_TYPES = ('text/plain', 'text/structured', 'text/x-rst', 'text/x-web-intelligent', )

# default mime type for textfields
#EC_DEFAULT_MIME_TYPE = 'text/x-web-intelligent'
EC_DEFAULT_MIME_TYPE = 'text/plain'

# default output format of textfields
#EC_DEFAULT_FORMAT = 'text/x-web-intelligent'
#EC_DEFAULT_FORMAT = 'text/html'
EC_DEFAULT_FORMAT = 'text/x-html-safe'

# extra permissions
GradeAssignments = 'eduComponents: Grade Assignments'
permissions.setDefaultRoles(GradeAssignments,  ('Manager',))

ViewAssignments = 'eduComponents: View Assignments'
permissions.setDefaultRoles(ViewAssignments,  ('Manager',))


# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
permissions.setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner'))
ADD_CONTENT_PERMISSIONS = {
    'ECFolder': 'ECAssignmentBox: Add ECFolder',
    'ECAssignmentBox': 'ECAssignmentBox: Add ECAssignmentBox',
    'ECAssignment': 'ECAssignmentBox: Add ECAssignment',
}

permissions.setDefaultRoles('ECAssignmentBox: Add ECFolder', ('Manager','Owner'))
permissions.setDefaultRoles('ECAssignmentBox: Add ECAssignmentBox', ('Manager','Owner'))
permissions.setDefaultRoles('ECAssignmentBox: Add ECAssignment', ('Manager','Owner'))
