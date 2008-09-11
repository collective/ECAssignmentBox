# -*- coding: utf-8 -*-
#
# File: ECAssignmentBox.py
#
# Copyright (c) 2008 by []
# Generator: ArchGenXML Version 2.1
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """unknown <unknown>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.ECAssignmentBox.config import *

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((


),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

ECAssignmentBox_schema = ATFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class ECAssignmentBox(ATFolder):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IECAssignmentBox)

    meta_type = 'ECAssignmentBox'
    _at_rename_after_creation = True

    schema = ECAssignmentBox_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

registerType(ECAssignmentBox, PROJECTNAME)
# end of class ECAssignmentBox

##code-section module-footer #fill in your manual code here
##/code-section module-footer



