# -*- coding: utf-8 -*-
# $Id: ECAssignmentBox.py 1296 2009-09-27 18:28:47Z amelung $
#
# Copyright (c) 2006-2009 Otto-von-Guericke University Magdeburg
#
# This file is part of ECAssignmentBox.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'
__version__   = '$Revision: 1.2 $'

import interfaces

from zope.interface import implements
from DateTime import DateTime

#from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema

from Products.Archetypes.atapi import Schema, BaseFolder, OrderedBaseFolder, \
    registerType
from Products.Archetypes.atapi import ReferenceField, TextField, DateTimeField, \
    IntegerField, BooleanField
from Products.Archetypes.atapi import RichWidget, TextAreaWidget, \
    CalendarWidget, IntegerWidget, BooleanWidget 

from Products.CMFCore.utils import getToolByName

#from Products.ATContentTypes.content.base import registerATCT
#from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget

from Products.ECAssignmentBox import config

import logging
log = logging.getLogger('ECAssignmentBox')

#ECAssignmentBox_schema = BaseBTreeFolderSchema.copy() + Schema((
ECAssignmentBox_schema = ATFolderSchema.copy() + Schema((
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
            i18n_domain = config.I18N_DOMAIN,
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
        allowable_content_types = config.EC_MIME_TYPES, 
        default_content_type = config.EC_DEFAULT_MIME_TYPE, 
        default_output_type = config.EC_DEFAULT_FORMAT,
        widget=RichWidget(
            label = 'Assignment text',
            label_msgid = 'label_assignment_text',
            description = 'Enter text and hints for the assignment',
            description_msgid = 'help_assignment_text',
            i18n_domain = config.I18N_DOMAIN,
            rows = 10,
            allow_file_upload = True,
        ),
    ),

    #PlainTextField('answerTemplate',
    TextField(
        'answerTemplate',
        searchable = True,
        allowable_content_types = ('text/plain',), #('text/x-web-intelligent',), 
        #default_content_type = EC_DEFAULT_MIME_TYPE, 
        #default_output_type = EC_DEFAULT_FORMAT,
        #widget=RichWidget(
        widget = TextAreaWidget(
            label = 'Answer template',
            label_msgid = 'label_answer_template',
            description = 'You can provide a template for the students\' answers',
            description_msgid = 'help_answer_template',
            i18n_domain = config.I18N_DOMAIN,
            rows = 12,
            #format = 0,
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
            i18n_domain = config.I18N_DOMAIN
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
            i18n_domain = config.I18N_DOMAIN,
        ),
    ),

    IntegerField('maxTries',
        searchable = False,
        required = True,
        default = 0,
        validators = ('isInt', 'isPositive'),
        widget = IntegerWidget(
            label = "Maximum number of attempts",
            label_msgid = "label_max_tries",
            description = "Maximum number of attempts, 0 means unlimited",
            description_msgid = "help_max_tries",
            i18n_domain = config.I18N_DOMAIN,
        ),
    ),

    BooleanField('wrapAnswer',
        default=True,
        widget=BooleanWidget(
            label="Enable word wrap in the Answer text area",
            description="If selected, text entered in the Answer field will be word-wrapped.  Disable word wrap if students are supposed to enter program code or similar notations.",
            label_msgid='label_wrapAnswer',
            description_msgid='help_wrapAnswer',
            i18n_domain=config.I18N_DOMAIN,
        ),
    ),

    BooleanField('sendNotificationEmail',
        default=False,
        widget=BooleanWidget(
            label="Send notification e-mail messages",
            description="If selected, the owner of this assignment box will receive an e-mail message each time an assignment is submitted.",
            label_msgid='label_sendNotificationEmail',
            description_msgid='help_sendNotificationEmail',
            i18n_domain=config.I18N_DOMAIN,
        ),
    ),
    
    BooleanField('sendGradingNotificationEmail',
        default=False,
        widget=BooleanWidget(
            label="Send grading notification e-mail messages",
            description="If selected, students will receive an e-mail message when their submissions to this assignment box are graded.",
            label_msgid='label_sendGradingNotificationEmail',
            description_msgid='help_sendGradingNotificationEmail',
            i18n_domain=config.I18N_DOMAIN,
        ),
    ),
                                                        
) # , marshall = PrimaryFieldMarshaller()
)

class ECAssignmentBox(ATFolder):
    """
    """
    typeDescription = 'Allows the creation, submission and grading ' \
                      'of online assignments.'
    typeDescMsgId   = 'description_edit_ecab'


    __implements__ = (ATFolder.__implements__)
    implements(interfaces.IECAssignmentBox)
    security = ClassSecurityInfo()

    meta_type = 'ECAssignmentBox'
    schema = ECAssignmentBox_schema
    _at_rename_after_creation = True
    
    ##code-section class-header #fill in your manual code here

    isAssignmentBoxType = True
    # FIXME: allowed_content_types is defined in profile.default.types.ECAssignmentBox.xml
    #        and should be used elsewhere
    allowed_content_types = ['ECAssignment']

    ##/code-section class-header

    # Methods
    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
        BaseFolder.manage_afterAdd(self, item, container)
        OrderedBaseFolder.manage_afterAdd(self, item, container)

        # Create a user-defined role "ECAssignment Viewer".  This role
        # has the View permission in certain states (defined in
        # ECAssignmentWorkflow).  This can be used for model
        # solutions: (1) Submit an assignment with the model
        # solution. (2) Use the "Sharing" tab to assign the role
        # "ECAssignment Viewer" to the users or groups who should be
        # allowed to view the assignment.
        #if 'ECAssignment Viewer' not in self.valid_roles():
        #    self.manage_defined_roles('Add Role',
        #                              {'role': 'ECAssignment Viewer'})

        # Create a user-defined role "ECAssignment Grader".  The owner
        # of an assignment box can use this role to delegate grading
        # to other users.
        #if 'ECAssignment Grader' not in self.valid_roles():
        #    self.manage_defined_roles('Add Role',
        #                              {'role': 'ECAssignment Grader'})

        # Plone 3: in profiles/default/rolemap.xml
        # Grant the GradeAssignments permission to the "ECAssignment
        # Grader" role.
        # self.manage_permission(permissions.GradeAssignments,
        #                       roles=['ECAssignment Grader',], acquire=True)
        
        # Assign the local roles to the creator
        creator = self.Creator()
        roles = list(self.get_local_roles_for_userid(creator))
        
        for role in ('ECAssignment Viewer', 'ECAssignment Grader'):
            if role not in roles:
                roles.append(role)
        
        self.manage_setLocalRoles(creator, roles)


    security.declarePublic('hasExpired')
    def hasExpired(self):
        now = DateTime()
        expiration_date = self.getSubmission_period_end()
        
        if ((expiration_date == None) or (expiration_date > now)):
            return False
        else:
            return True

    security.declarePublic('isEffective')
    def isEffective(self):
        now = DateTime()
        effective_date = self.getSubmission_period_start()

        if ((effective_date != None) and (effective_date > now)):
            return False
        else:
            return True


    security.declarePublic('getTries')
    def getTries(self):
        """
        EXPERIMENTAL.  Return the number of submissions of the current
        user.
        """
        
        user_id = self.portal_membership.getAuthenticatedMember().getId()
        catalog = getToolByName(self, 'portal_catalog')

        brains = catalog.searchResults(
            path          = {'query': '/'.join(self.getPhysicalPath()),
                             'depth': 1,},
            Creator       = user_id,
            contentFilter = {'portal_type': self.allowed_content_types},
        )

        return len(brains)


    security.declarePublic('canSupersed')
    def canSupersed(self):
        """
        Return whether submissions are possible.  Submissions are not
        possible if there is an assignment which cannot be superseded.
        """
        
        wtool = self.portal_workflow
        catalog = getToolByName(self, 'portal_catalog')
        
        member = self.portal_membership.getAuthenticatedMember()

        brains = catalog.searchResults(
            path          = {'query': '/'.join(self.getPhysicalPath()), 'depth': 1,},
            Creator       = member.getId(),
            contentFilter = {'portal_type': self.allowed_content_types},
        )
        
        for brain in brains:
            if brain.review_state != 'superseded':
                a = brain.getObject()
                wf = wtool.getWorkflowsFor(a)[0]

                if not wf.isActionSupported(a, 'supersede'):
                    return False
        
        return True

    
    security.declarePublic('canRetry')
    def canRetry(self):
        """
        Return whether submissions are possible.  Submissions are not
        possible if the maximum number of tries has been reached.
        """

        catalog = getToolByName(self, 'portal_catalog')
        
        member = self.portal_membership.getAuthenticatedMember()

        brains = catalog.searchResults(
            path          = {'query': '/'.join(self.getPhysicalPath()), 'depth': 1,},
            Creator       = member.getId(),
            contentFilter = {'portal_type': self.allowed_content_types},
        )
        
        if self.getMaxTries() and len(brains) >= self.getMaxTries():
            return False
        
        return True


    def getGradeForStudent(self, student):
        """
        FIXME: currently unused!
        TODO: use portal_catalog
        """
        submissions = self.contentValues(filter={'Creator': student})
        if submissions:
            submission = submissions[0]
            field = submission.getField('mark')
            return field.getAccessor(submission)()


    def getGradesByStudent(self):
        """
        Collect the grades for all assignments in this box which are
        in the `graded' state and which were assigned a *numeric*
        grade.  Return an empty dictionary if no grades were assigned.
        Return a dictionary with student: grade entries if grades were
        assigned.  Return None if non-numeric grades were assigned.

        @return a dictionary with user ID as key and grade as value
        """
        wtool = self.portal_workflow
        items = self.contentValues()
        summary = {}

        for item in items:
            if wtool.getInfoFor(item, 'review_state') == 'graded' \
                   and item.mark:
                try:
                    summary[item.Creator()] = float(item.mark)
                except ValueError:
                    return None

        return summary

    def getNumericGrades(self):
        """
        @return a list containing all grades assigned to graded
        submissions in this box
        """
        wtool = self.portal_workflow
        items = self.contentValues(filter={'portal_type':
                                           self.allowed_content_types})
        grades = []

        for item in items:
            state = wtool.getInfoFor(item, 'review_state')
            if state not in ('graded'):
                continue

            if not item.mark:
                continue

            grades.append(item.mark)

        for i in range(0, len(grades)):
            try:
                grades[i] = float(grades[i])
            except ValueError:
                return None

        return grades


    #security.declarePrivate('getNotificationEmailAddresses')
    def getNotificationEmailAddresses(self):
        """
        Get the e-mail addresses to which notification messages should
        be sent.  May return an empty list if notification is turned
        off.  Currently returns only the address of the owner of the
        assignment box.
        """
        if not self.getSendNotificationEmail():
            return []

        putils = getToolByName(self, 'plone_utils')
        ecab_utils = getToolByName(self, 'ecab_utils')

        addresses = []
        addresses.append(ecab_utils.getUserPropertyById(
                                        putils.getOwnerName(self), 'email'))

        return addresses



registerType(ECAssignmentBox, config.PROJECTNAME)
