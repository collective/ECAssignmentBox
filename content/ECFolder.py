# -*- coding: utf-8 -*-
#
# File: ECFolder.py
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

    StringField(
        name='directions',
        widget=RichWidget(
            label="Directions",
            description="Location for this course",
            label_msgid="label_location",
            description_msgid="help_location",
            i18n_domain=I18N_DOMAIN,
        ),
    ),
    IntegerField(
        name='projectedAssignments',
        widget=IntegerWidget(
            label="Projected Number of Assignments",
            description="Enter the type of this course (e.g., Lecture or Lab Exercise)",
            label_msgid="label_course_type",
            description_msgid="help_course_type",
            i18n_domain=I18N_DOMAIN,
        ),
        searchable=0,
    ),
    LinesField(
        name='completedStates',
        widget=LinesWidget(
            label="Instructors",
            description="User names or names of instructors, one per line",
            label_msgid="label_instructors",
            description_msgid="help_instructors",
            i18n_domain=I18N_DOMAIN,
        ),
        languageIndependent=True,
        searchable=True,
        required=True,
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

ECFolder_schema = ATFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class ECFolder(ATFolder):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IECFolder)

    meta_type = 'ECFolder'
    _at_rename_after_creation = True

    schema = ECFolder_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

registerType(ECFolder, PROJECTNAME)
# end of class ECFolder

##code-section module-footer #fill in your manual code here
##/code-section module-footer



