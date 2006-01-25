# -*- coding: utf-8 -*-
# $Id$
#
# Copyright (c) 2005 Otto-von-Guericke-Universität Magdeburg
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

__author__    = '''ma <amelung@iws.cs.uni-magdeburg.de>'''
__docformat__ = 'plaintext'
__version__   = '$Revision$'

import os, os.path

import ECAssignmentWorkflow

from Globals import package_home

from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory

from Products.ECAssignmentBox.config import SKINS_DIR, GLOBALS, PROJECTNAME
from Products.ECAssignmentBox.config import ADD_CONTENT_PERMISSION

registerDirectory(SKINS_DIR, GLOBALS)

def initialize(context):
    # Import Types here to register them
    import ECFolder, ECAssignmentBox

    from AccessControl import ModuleSecurityInfo
    from AccessControl import allow_module, allow_class, allow_type

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)
    
    utils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)

    # Tools
    import ECABTool
    from Products.CMFPlone.utils import ToolInit

    tools = (ECABTool.ECABTool,)
    
    ToolInit(PROJECTNAME + ' Tool',
             tools = tools,
             product_name = PROJECTNAME,
             icon = 'tool.png'
             ).initialize(context)
