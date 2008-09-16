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
    FileField(
        'file',
        searchable = True,
        primary = True,
        widget = FileWidget(
            label = "Answer",
            label_msgid = "label_answer",
            description = "The submission for this assignment",
            description_msgid = "help_answer",
            i18n_domain = I18N_DOMAIN,
            macro = 'answer_widget',
        ),
    ),

    TextField(
        'remarks',
        default_content_type = 'text/structured',
        default_output_type = 'text/html',
        allowable_content_types = TEXT_TYPES,
        widget = TextAreaWidget(
            label = "Remarks",
            label_msgid = "label_remarks",
            description = "Your remarks for this assignment (they will not be shown to the student)",
            description_msgid = "help_remarks",
            i18n_domain = I18N_DOMAIN,
            rows = 8,
        ),
        read_permission = permissions.ModifyPortalContent,
    ),

    TextField(
        'feedback',
        searchable = True,
        default_content_type = 'text/structured',
        default_output_type = 'text/html',
        allowable_content_types = TEXT_TYPES,
        widget = TextAreaWidget(
            label = "Feedback",
            label_msgid = "label_feedback",
            description = "The grader's feedback for this assignment",
            description_msgid = "help_feedback",
            i18n_domain = I18N_DOMAIN,
            rows = 8,
        ),
    ),

    StringField(
        'mark',
        #searchable = True,
        accessor = 'getGradeIfAllowed',
        edit_accessor = 'getGradeForEdit',
        mutator = 'setGrade',
        widget=StringWidget(
            label = 'Grade',
            label_msgid = 'label_grade',
            description = "The grade awarded for this assignment",
            description_msgid = "help_grade",
            i18n_domain = I18N_DOMAIN,
        ),
    ),

),
)

##code-section after-local-schema #fill in your manual code here
# alter default fields -> hide title and description

# FIXME: add method _generateTitle
schema['title'].default_method = '_generateTitle'
schema['title'].widget.visible = {
    'view' : 'invisible',
    'edit' : 'invisible'
}
schema['description'].widget.visible = {
    'view' : 'invisible',
    'edit' : 'invisible'
}
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



