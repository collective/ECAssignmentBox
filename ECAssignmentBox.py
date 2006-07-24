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
from hotshot import log

from DateTime import DateTime

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName

from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.base import updateActions, updateAliases
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.ATContentTypes.content.folder import ATFolder

# local imports
from Products.ECAssignmentBox.config import *
from Products.ECAssignmentBox import permissions
from Products.ECAssignmentBox.ECAssignment import ECAssignment
from Products.ECAssignmentBox.interfaces.IECSubmissionsContainer \
     import IECSubmissionsContainer
from Statistics import Statistics

from Products.ECAssignmentBox.PlainTextField import PlainTextField

ECAssignmentBoxSchema = ATFolderSchema.copy() + Schema((
    TextField(
        'assignment_text',
        required=True,
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
                                                        
) # , marshall = PrimaryFieldMarshaller()
)

finalizeATCTSchema(ECAssignmentBoxSchema, folderish=True, moveDiscussion=False)

class ECAssignmentBox(ATFolder):
    """Allows the creation, submission and grading of online assignments"""

    __implements__ = (ATFolder.__implements__) + (IECSubmissionsContainer,)

    security = ClassSecurityInfo()

    schema = ECAssignmentBoxSchema

    content_icon = "ecab.png"
    portal_type = meta_type = ECAB_META
    archetype_name = ECAB_NAME

    filter_content_types = 1
    allowed_content_types = [ECAssignment.meta_type]

    suppl_views = None
    default_view = 'ecab_view'
    immediate_view = 'ecab_view'

    typeDescription = 'Allows the creation, submission and grading ' \
                      'of online assignments.'
    typeDescMsgId   = 'description_edit_ecab'

    _at_rename_after_creation = True

    # -- actions --------------------------------------------------------------
    actions = updateActions(ATFolder, (
        {
        'action':      "string:$object_url/all_assignments",
        'category':    "object",
        'id':          'all_assignments',
        'name':        'Assignments',
        'permissions': (permissions.View,),
        # Only display the assignments tab if there actually are assignments
        'condition':   'python: len(here.contentValues()) > 0'
        },

        {
        'action':      'string:ecab_compare_assignments:method',
        'id':          'ecab_compare_assignments',
        'name':        'Compare Two Assignments',
        'permissions': (permissions.View,),
        'category':    'folder_buttons',
        },
    ))
    
    aliases = updateAliases(ATFolder, {
        'view': 'ecab_view',
        })

    # -- methods --------------------------------------------------------------
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
        if 'ECAssignment Viewer' not in self.valid_roles():
            self.manage_defined_roles('Add Role',
                                      {'role': 'ECAssignment Viewer'})

        # Create a user-defined role "ECAssignment Grader".  The owner
        # of an assignment box can use this role to delegate grading
        # to other users.
        if 'ECAssignment Grader' not in self.valid_roles():
            self.manage_defined_roles('Add Role',
                                      {'role': 'ECAssignment Grader'})

        # Grant the GradeAssignments permission to the "ECAssignment
        # Grader" role.
        self.manage_permission(permissions.GradeAssignments,
                               roles=['ECAssignment Grader',], acquire=True)
        
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

    security.declarePublic('canResubmit')
    def canResubmit(self):
        user_id = self.portal_membership.getAuthenticatedMember().getId()
        wtool = self.portal_workflow
        
        assignments = self.contentValues(filter = {'Creator': user_id})
        
        for a in assignments:
            wf = wtool.getWorkflowsFor(a)[0]
            if wf.getInfoFor(a, 'review_state', '') != 'superseded' \
                   and not wf.isActionSupported(a, 'supersede'):
                return False
        
        return True

    def getAssignmentsSummary(self, id=None):
        items = self.contentValues(filter={'portal_type':
                                           self.allowed_content_types})
        items.sort(lambda a, b: cmp(a.CreationDate(), b.CreationDate()))
        wtool = self.portal_workflow
        current_user = self.portal_membership.getAuthenticatedMember()
        summary = []
        
        for item in items:
            if (current_user.checkPermission(permissions.View, item)):
                if id and item.Creator() != id:
                    continue
                summary.append(item)
        return summary

    def getGradeForStudent(self, student):
        """
        Your documentation here
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
        Add documentation here

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


    security.declarePrivate('getNotificationEmailAddresses')
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
        
        addresses = []
        addresses.append(self.ecab_utils.getUserPropertyById(
                                         putils.getOwnerName(self), 'email'))
       
        return addresses


registerATCT(ECAssignmentBox, PROJECTNAME)