# -*- coding: utf-8 -*-
# $Id$
#
# Copyright (c) 2006-2008 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECAssignmentBox.
#
# ECAssignmentBox is free software; you can redistribute it and/or 
# modify it under the terms of the GNU General Public License as 
# published by the Free Software Foundation; either version 2 of the 
# License, or (at your option) any later version.
#
# ECAssignmentBox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ECAssignmentBox; if not, write to the 
# Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, 
# MA  02110-1301  USA
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'
__version__   = '$Revision$'

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
