# -*- coding: utf-8 -*-
#
# File: ECABTool.py
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


from Products.CMFCore.utils import UniqueObject

    
##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((


),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

ECABTool_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class ECABTool(UniqueObject, BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IECABTool)

    meta_type = 'ECABTool'
    _at_rename_after_creation = True

    schema = ECABTool_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header


    # tool-constructors have no id argument, the id is fixed
    def __init__(self, id=None):
        BaseContent.__init__(self,'portal_ecabtool')
        self.setTitle('')
        
        ##code-section constructor-footer #fill in your manual code here
        ##/code-section constructor-footer


    # tool should not appear in portal_catalog
    def at_post_edit_script(self):
        self.unindexObject()
        
        ##code-section post-edit-method-footer #fill in your manual code here
        ##/code-section post-edit-method-footer


    # Methods
    #security.declarePrivate('getWfStates')
    def getWfStates(self, wfName=ECA_WORKFLOW_ID):
        """
        @return a list containing all state keys in assignment's workflow
        """
        wtool = self.portal_workflow
        return wtool.getWorkflowById(wfName).states.keys()

    #security.declarePrivate('getWfStatesDisplayList')
    def getWfStatesDisplayList(self, wfName=ECA_WORKFLOW_ID):
        """
        @return a DisplayList containing all state keys and state titles in 
                assignment's workflow
        """
        dl = DisplayList(())

        wtool = self.portal_workflow
        wf = wtool.getWorkflowById(wfName)
        stateKeys = self.getWfStates(wfName)
        
        for key in stateKeys:
            dl.add(key, wf.states[key].title)

        #return dl.sortedByValue()
        return dl

registerType(ECABTool, PROJECTNAME)
# end of class ECABTool

##code-section module-footer #fill in your manual code here
##/code-section module-footer



