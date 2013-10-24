# -*- coding: utf-8 -*-
# $Id: ECFolder.py 1570 2011-06-28 22:33:33Z amelung $
#
# Copyright (c) 2006-2011 Otto-von-Guericke-UniversitŠt Magdeburg
#
# This file is part of ECAssignmentBox.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'

import interfaces

from AccessControl import ClassSecurityInfo
from zope.interface import implements

from Products.Archetypes.atapi import Schema, registerType, DisplayList
from Products.Archetypes.atapi import TextField, LinesField, IntegerField
from Products.Archetypes.atapi import RichWidget, MultiSelectionWidget, \
    IntegerWidget

from Products.CMFCore.utils import getToolByName
#from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema

from Products.ECAssignmentBox.content import validators
from Products.ECAssignmentBox import config
from Products.ECAssignmentBox import LOG


schema = Schema((

    TextField(
        'directions',
        allowable_content_types = config.ALLOWED_CONTENT_TYPES, 
        default_content_type = config.DEFAULT_CONTENT_TYPE, 
        default_output_type = config.DEFAULT_OUTPUT_TYPE,
        widget = RichWidget(
            label = 'Directions',
            label_msgid = 'label_directions',
            description = 'Instructions/directions that all assignment boxes in this folder refer to',
            description_msgid = 'help_directions',
            i18n_domain = config.I18N_DOMAIN,
            allow_file_upload = False,
            rows = 8,
        ),
    ),

    LinesField(
        'completedStates',
        searchable = False,
        vocabulary = 'getCompletedStatesVocab',
        multiValued = True,
        widget = MultiSelectionWidget(
            label = "Completed States",
            label_msgid = "label_completed_states",
            description = "States considered as completed",
            description_msgid = "help_completed_states",
            i18n_domain = config.I18N_DOMAIN,
        ),
    ),

    IntegerField(
        'projectedAssignments',
        searchable = False,
        required = True,
        default = 0,
        validators = ('isInt', validators.POSITIVE_NUMBER_VALIDATOR_NAME),
        widget = IntegerWidget(
            label = "Projected Number of Assignments",
            label_msgid = "label_projected_assignments",
            description = "Projected number of assignments, 0 means undefined",
            description_msgid = "help_projected_assignments",
            i18n_domain = config.I18N_DOMAIN,
        ),
    ),

),
)

ECFolder_schema = ATFolderSchema.copy() + schema.copy()

class ECFolder(ATFolder):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IECFolder)

    meta_type = 'ECFolder'
    _at_rename_after_creation = True

    schema = ECFolder_schema

    # Methods
    security.declarePrivate('getCompletedStatesVocab')
    def getCompletedStatesVocab(self):
        """
        HINT: used as vocabulary for completedStates only (s. a.)
        """
        ecab_utils = getToolByName(self, 'ecab_utils', None)
        return ecab_utils.getWfStatesDisplayList(config.ECA_WORKFLOW_ID)

    
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
        result = {}
        
        # get current uses's id
        currentUser = self.portal_membership.getAuthenticatedMember()
        # check if current user is owner of this folder
        isOwner = currentUser.has_role(['Owner', 'Reviewer', 'Manager'], self)
        
        catalog = getToolByName(self, 'portal_catalog')

        if isOwner:
            brains = catalog.searchResults(path = {'query':'/'.join(self.getPhysicalPath()), 'depth':100, },
                                   isAssignmentType = True,
                                   )
        else:
            brains = catalog.searchResults(path = {'query':'/'.join(self.getPhysicalPath()), 'depth':100, },
                                   Creator = currentUser.getId(), 
                                   isAssignmentType = True,
                                   )

        wf_states = self.getWfStates()
        
        #LOG.debug('wf_states: %s' % wf_states)
        
        n_states = len(wf_states)
    
        for brain in brains:
            key = brain.Creator
            reviewState = brain.review_state
            
            if key and reviewState: 
                #LOG.debug('key: %s' % key)
                #LOG.debug('reviewState: %s' % reviewState)
                
                if not result.has_key(key):
                    result[key] = [0 for i in range(n_states)]
                    
                LOG.debug('result: %s' % result)
                
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
            
            #LOG.debug('xxx: %s: %s' % (item.title, grades, ))

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
        #mtool = self.portal_membership

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
            return ecab_utils.getWfStates(config.ECA_WORKFLOW_ID)
        else:
            LOG.warn("Could not get tool by name: '%s'" % 'ecab_utils')
            return ()


    security.declarePublic('getWfTransitionsDisplayList')
    def getWfTransitionsDisplayList(self):
        """
        @deprecated use getWfTransitionsDisplayList in ecab_utils directly
        """
        ecab_utils = getToolByName(self, 'ecab_utils', None)
        
        if (ecab_utils != None):
            return ecab_utils.getWfTransitionsDisplayList(config.ECA_WORKFLOW_ID)
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
        
        #LOG.info('xxx: %s' % self.aq_explicit)
        
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


registerType(ECFolder, config.PROJECTNAME)
