# -*- coding: utf-8 -*-
# $Id$
#
# Copyright (c) 2006 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECAssignmentBox.
#
# ECAssignmentBox is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ECAssignmentBox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ECAssignmentBox; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from Products.CMFCore.permissions import setDefaultRoles, AddPortalContent
from Products.Archetypes.public import DisplayList

GLOBALS = globals()

I18N_DOMAIN = 'eduComponents'

# define product and tool names
PROJECTNAME = "ECAssignmentBox"

ECAB_META = "ECAssignmentBox"
ECAB_NAME = "Assignment Box"

ECA_META = "ECAssignment"
ECA_NAME = "Assignment"

ECA_WORKFLOW_ID = 'ec_assignment_workflow'
ECA_WORKFLOW_TITLE= 'Assignment workflow [EC]'


SKINS_DIR = 'skins'

DEPENDENCIES = ['Archetypes',]

TOOL_NAME  = "ecab_utils"
TOOL_META  = "ECAssignmentBox Utility Tool"
TOOL_TITLE = "Assignment Box Settings"
TOOL_ICON  = "ec_tool.png"

# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = AddPortalContent
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner',))

ADD_CONTENT_PERMISSIONS = {
    'ECFolder':        'eduComponents: Add ECFolder',
    'ECAssignmentBox': 'eduComponents: Add Assignment Box',
}

setDefaultRoles('eduComponents: Add ECFolder',       ('Manager', 'Owner',))
setDefaultRoles('eduComponents: Add Assignment Box', ('Manager', 'Owner',))

# Supported formats in text areas
TEXT_TYPES = (
    'text/structured',
    'text/x-rst',
    'text/html',
    'text/plain',
    )

# Some LOG levels
BLATHER=-100
DEBUG=-200
TRACE=-300
    
