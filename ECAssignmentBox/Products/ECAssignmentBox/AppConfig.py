# -*- coding: utf-8 -*-
# $Id: AppConfig.py 1297 2009-09-27 18:29:20Z amelung $
#
# Copyright (c) 2006-2009 Otto-von-Guericke University Magdeburg
#
# This file is part of ECAssignmentBox.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'
__version__   = '$Revision: 1.2 $'

try: # New CMF 
    from Products.CMFCore import permissions
except: # Old CMF 
    from Products.CMFCore import CMFCorePermissions as permissions

# i18n 
I18N_DOMAIN = 'eduComponents'

# dependencies of products to be installed by quick-installer
DEPENDENCIES = []
# Plone 3.x has plone.intelligenttext already.  Lower versions
# need Products.intelligenttext installed as a dependency here.
#DEPENDENCIES = ['intelligenttext']

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
