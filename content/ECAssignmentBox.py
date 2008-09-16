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
    ReferenceField(
        'assignment_reference',
        allowed_types = ('ECAssignmentTask',),
        required = False,
        accessor = 'getReference',
        index = "FieldIndex:schema", # Adds "getRawAssignment_reference"
                                     # to catalog
        multiValued = False,
        relationship = 'alter_ego',
        widget = ReferenceBrowserWidget(
            description = 'Select an assignment task.  A reference to an assignment task supersedes the assignment text and answer template below.',
            description_msgid = 'help_assignment_reference',
            i18n_domain = I18N_DOMAIN,
            label = 'Reference to assignment',
            label_msgid = 'label_assignment_reference',
            allow_search = True,
            show_indexes = False,
        ),
    ),
    TextField(
        'assignment_text',
        required = False,
        searchable = True,
        default_output_type = 'text/html',
        default_content_type = 'text/structured',
        allowable_content_types = TEXT_TYPES,
        widget=RichWidget(
            label = 'Assignment text',
            label_msgid = 'label_assignment_text',
            description = 'Enter text and hints for the assignment',
            description_msgid = 'help_assignment_text',
            i18n_domain = I18N_DOMAIN,
            rows=10,
        ),
    ),

    PlainTextField('answerTemplate',
        widget=RichWidget(
            label = 'Answer template',
            label_msgid = 'label_answer_template',
            description = 'You can provide a template for the students\' answers',
            description_msgid = 'help_answer_template',
            i18n_domain = I18N_DOMAIN,
            rows = 12,
            format = 0,
        ),
    ),

    DateTimeField(
        'submission_period_start',
        #mutator = 'setEffectiveDate',
        languageIndependent = True,
        #default=FLOOR_DATE,
        widget = CalendarWidget(
            label = "Start of Submission Period",
            description = ("Date after which students are allowed to "
                           "submit their assignments"),
            label_msgid = "label_submission_period_start",
            description_msgid = "help_submission_period_start",
            i18n_domain = I18N_DOMAIN
        ),
    ),
    
    DateTimeField(
        'submission_period_end',
        #mutator = 'setExpirationDate',
        languageIndependent = True,
        #default=CEILING_DATE,
        widget = CalendarWidget(
            label = "End of Submission Period",
            description = ("Date after which assignments can no longer "
                           "be submitted"),
            label_msgid = "label_submission_period_end",
            description_msgid = "help_submission_period_end",
            i18n_domain = I18N_DOMAIN,
        ),
    ),

    IntegerField('maxTries',
        searchable = False,
        required = True,
        default = 0,
        # FIXME: validators = ('isInt', 'isPositive'),
        widget = IntegerWidget(
            label = "Maximum number of attempts",
            label_msgid = "label_max_tries",
            description = "Maximum number of attempts, 0 means unlimited",
            description_msgid = "help_max_tries",
            i18n_domain = I18N_DOMAIN,
        ),
    ),

    BooleanField('wrapAnswer',
        default=True,
        widget=BooleanWidget(
            label="Enable word wrap in the Answer text area",
            description="If selected, text entered in the Answer field will be word-wrapped.  Disable word wrap if students are supposed to enter program code or similar notations.",
            label_msgid='label_wrapAnswer',
            description_msgid='help_wrapAnswer',
            i18n_domain=I18N_DOMAIN,
        ),
    ),

    BooleanField('sendNotificationEmail',
        default=False,
        widget=BooleanWidget(
            label="Send notification e-mail messages",
            description="If selected, the owner of this assignment box will receive an e-mail message each time an assignment is submitted.",
            label_msgid='label_sendNotificationEmail',
            description_msgid='help_sendNotificationEmail',
            i18n_domain=I18N_DOMAIN,
        ),
    ),
    
    BooleanField('sendGradingNotificationEmail',
        default=False,
        widget=BooleanWidget(
            label="Send grading notification e-mail messages",
            description="If selected, students will receive an e-mail message when their submissions to this assignment box are graded.",
            label_msgid='label_sendGradingNotificationEmail',
            description_msgid='help_sendGradingNotificationEmail',
            i18n_domain=I18N_DOMAIN,
        ),
    ),
                                                        
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



