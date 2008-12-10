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

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces

from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.ECAssignmentBox.config import *

##code-section module-header #fill in your manual code here

import logging
log = logging.getLogger('ECAssignmentBox')

##/code-section module-header

schema = Schema((

    TextField(
        'directions',
        allowable_content_types = EC_MIME_TYPES, 
        default_content_type = EC_DEFAULT_MIME_TYPE, 
        default_output_type = EC_DEFAULT_FORMAT,
        widget = RichWidget(
            label = 'Directions',
            label_msgid = 'label_directions',
            description = 'Instructions/directions that all assignment boxes in this folder refer to',
            description_msgid = 'help_directions',
            i18n_domain = I18N_DOMAIN,
            allow_file_upload = False,
            rows = 8,
        ),
    ),

    LinesField(
        'completedStates',
        searchable = False,
        vocabulary = 'getWfStatesDisplayList',
        multiValued = True,
        widget = MultiSelectionWidget(
            label = "Completed States",
            label_msgid = "label_completed_states",
            description = "States considered as completed",
            description_msgid = "help_completed_states",
            i18n_domain = I18N_DOMAIN,
        ),
    ),

    IntegerField(
        'projectedAssignments',
        searchable = False,
        required = True,
        default = 0,
        #validators = ('isInt', 'isPositive'),
        widget = IntegerWidget(
            label = "Projected Number of Assignments",
            label_msgid = "label_projected_assignments",
            description = "Projected number of assignments, 0 means undefined",
            description_msgid = "help_projected_assignments",
            i18n_domain = I18N_DOMAIN,
        ),
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

ECFolder_schema = ATFolderSchema.copy() + schema.copy()

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
    #security.declarePrivate('getWfStatesDisplayList')
    def getWfStatesDisplayList(self):
        """
        @deprecated use getWfStatesDisplayList in ecab_utils directly
        """
#        try:
#            utils = getToolByName(self, 'ecab_utils')
#            return utils.getWfStatesDisplayList(ECA_WORKFLOW_ID)
#        except AttributeError:
#            return DisplayList(())
        ecab_utils = getToolByName(self, 'ecab_utils', None)
        
        if (ecab_utils != None):
            return ecab_utils.getWfStatesDisplayList(ECA_WORKFLOW_ID)
        else:
            return DisplayList(())

    
    security.declarePublic('summarize')
    def summarize(self):
        """
        Returns an dictionary containing summarized states of all assignments 
        for current user - or all users if manager - in all subfolders.
        
        Only users with roles owner, reviewer or manager will see 
        summarized states of all users.
        
        @return a dictionary containing user-id as key and summarized states
                as value
        """
        
        # get current uses's id
        currentUser = self.portal_membership.getAuthenticatedMember()
        # check if current user is owner of this folder
        isOwner = currentUser.has_role(['Owner', 'Reviewer', 'Manager'], self)
        
        catalog = getToolByName(self, 'portal_catalog')

        if isOwner:
            brains = catalog.searchResults(path = {'query':'/'.join(self.getPhysicalPath()), 'depth':100, },
                                   #meta_type = (ECA_META, 'ECAutoAssignment', ),
                                   isAssignmentType = True,
                                   )
        else:
            brains = catalog.searchResults(path = {'query':'/'.join(self.getPhysicalPath()), 'depth':100, },
                                   Creator = currentUser.getId(), 
                                   #meta_type = (ECA_META, 'ECAutoAssignment', ),
                                   isAssignmentType = True,
                                   )

        wf_states = self.getWfStates()
        n_states = len(wf_states)
    
        result = {}

        for brain in brains:
            key = brain.Creator

            if not result.has_key(key):
                result[key] = [0 for i in range(n_states)]
            
            result[key][wf_states.index(brain.review_state)] += 1

        return result


    security.declarePublic('summarizeGrades')
    def summarizeGrades(self, published=True):
        """
        Create a dictionary listing all grades for the contained
        assignments by student, i.e., the keys are user IDs, the
        values are lists of grades.  Example:

        {'freddy': [3.0, 3.0], 'dina': [2.0, 2.0, 2.0]}
        
        @return a dictionary
        """

        """
        wtool = self.portal_workflow
        items = self.contentValues(filter={'portal_type': 
                                            self.allowed_content_types})
        students = {}
        
        for item in items:
            if published:
                review_state = wtool.getInfoFor(item, 'review_state')
                if review_state not in ('published'):
                    continue
            
            grades = {}
            
            if item.portal_type == 'ECFolder':
                grades = item.summarizeGrades(published)
            elif self.ecab_utils.testAssignmentBoxType(item):
                grades = item.getGradesByStudent()

            # No grades were assigned--no problem.
            if grades == {}:
                continue
            
            # Non-numeric grades were assigned: Immediately return,
            # as we can't calculate meaningful statistics in this
            # case.
            if grades == None:
                return {}
            
            for student in grades:
                if student not in students:
                    students[student] = []
                if type(grades[student]) is list:
                    students[student].extend(grades[student])
                else:
                    students[student].append(grades[student])
            
        return students
        """
       
        catalog = getToolByName(self, 'portal_catalog')

        if published:
            brains = catalog.searchResults(path = {'query':'/'.join(self.getPhysicalPath()), 'depth':100, },
                                           review_state = 'published',
                                           isAssignmentBoxType = True,
                                           )
        else:
            brains = catalog.searchResults(path = {'query':'/'.join(self.getPhysicalPath()), 'depth':100, },
                                           isAssignmentBoxType = True,
                                          )
        students = {}
        
        for brain in brains:
            item = brain.getObject()
            grades = {}
            
            grades = item.getGradesByStudent()
            
            #log.debug('xxx: %s: %s' % (item.title, grades, ))

            # No grades were assigned--no problem.
            if grades == {}:
                continue
            
            # Non-numeric grades were assigned: Immediately return,
            # as we can't calculate meaningful statistics in this
            # case.
            if grades == None:
                return {}
            
            for student in grades:
                if student not in students:
                    students[student] = []
                if type(grades[student]) is list:
                    students[student].extend(grades[student])
                else:
                    students[student].append(grades[student])
            
        return students

    
    security.declarePublic('rework')
    def rework(self, dict):
        """
        Returns an array which consists of a dict with full name and summarized
        assignment states.
        
        @param dict summarized assignments
        @return an array
        """
        array = []
        mtool = self.portal_membership

        for key in dict:
            array.append((key, self.ecab_utils.getFullNameById(key),
                          dict[key]))
            array.sort(lambda a, b: cmp(a[1], b[1]))

        return array


    security.declarePublic('summarizeCompletedAssignments')
    def summarizeCompletedAssignments(self, summary=None):
        """
        Returns a dictionary containing the number of assignments
        in a completed state per student.
        
        @param summary 
        @return a dictionary
        """
        if not self.completedStates:
            return None

        if not summary:
            summary = self.summarize()
        
        states = self.getWfStates()
        retval = {}

        for student in summary.keys():
            state_no = 0
            retval[student] = 0

            for num in summary[student]:
                if states[state_no] in self.completedStates and num > 0:
                    retval[student] += num
                state_no += 1
        return retval


    security.declarePublic('getWfStates')
    def getWfStates(self):
        """
        @deprecated use getWfStates in ecab_utils directly
        """
        ecab_utils = getToolByName(self, 'ecab_utils', None)
        
        if (ecab_utils != None):
            return ecab_utils.getWfStates(ECA_WORKFLOW_ID)
        else:
            return ()


    security.declarePublic('getWfTransitionsDisplayList')
    def getWfTransitionsDisplayList(self):
        """
        @deprecated use getWfTransitionsDisplayList in ecab_utils directly
        """
        ecab_utils = getToolByName(self, 'ecab_utils', None)
        
        if (ecab_utils != None):
            return ecab_utils.getWfTransitionsDisplayList(ECA_WORKFLOW_ID)
        else:
            return DisplayList(())


    security.declarePublic('countContainedBoxes')
    def countContainedBoxes(self, published=True):
        """
        Count the assignment boxes contained in this folder and its
        subfolders.  By default, only published boxes and folders are
        considered.  Set published=False to count all boxes.

        @param published 
        @return an integer
        """
        brains = []
        
        # get the portal's catalog
        catalog = getToolByName(self, 'portal_catalog')

        # get all items inside this ecfolder
        if published:
            #, 'depth':100
            brains = catalog.searchResults(path = {'query':'/'.join(self.getPhysicalPath()), 'depth':100, }, 
                                           #sort_on = 'getObjPositionInParent', 
                                           review_state = 'published',
                                           #meta_type = (ECAB_META, 'ECAutoAssignmentBox', ),
                                           isAssignmentBoxType = True,
                                           )
        else:
            brains = catalog.searchResults(path = {'query':'/'.join(self.getPhysicalPath()), },
                                           #sort_on = 'getObjPositionInParent', 
                                           #meta_type = (ECAB_META, 'ECAutoAssignmentBox', ),
                                           isAssignmentBoxType = True,
                                           )
        return len(brains)


registerType(ECFolder, PROJECTNAME)
