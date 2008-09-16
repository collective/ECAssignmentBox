# -*- coding: utf-8 -*-
# $Id$
#
# Copyright (c) 2008 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECAssignmentBox.
#
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

    TextField(
        'directions',
        default_content_type = 'text/structured',
        default_output_type = 'text/html',
        allowable_content_types = TEXT_TYPES,
        widget = RichWidget(
            label = 'Directions',
            label_msgid = 'label_directions',
            description = 'Instructions/directions that all assignment boxes in this folder refer to',
            description_msgid = 'help_directions',
            i18n_domain = I18N_DOMAIN,
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
    #security.declarePrivate('getWfStatesDisplayList')
    def getWfStatesDisplayList(self):
        """
        @deprecated use getWfStatesDisplayList in ecab_utils instead
        """
        #utils = self.ecab_utils
        utils = self.portal_ecabtool
        return utils.getWfStatesDisplayList(ECA_WORKFLOW_ID)


registerType(ECFolder, PROJECTNAME)
# end of class ECFolder

##code-section module-footer #fill in your manual code here
##/code-section module-footer



