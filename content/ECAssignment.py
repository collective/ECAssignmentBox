# -*- coding: utf-8 -*-
#
# File: ECAssignment.py
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

from Products.ECAssignmentBox.config import *

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((


),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

ECAssignment_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class ECAssignment(BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IECAssignment)

    meta_type = 'ECAssignment'
    _at_rename_after_creation = True

    schema = ECAssignment_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

registerType(ECAssignment, PROJECTNAME)
# end of class ECAssignment

##code-section module-footer #fill in your manual code here
##/code-section module-footer



