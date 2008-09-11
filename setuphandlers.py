# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
#
# Copyright (c) 2008 by []
# Generator: ArchGenXML Version 2.1
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """unknown <unknown>"""
__docformat__ = 'plaintext'


import logging
logger = logging.getLogger('ECAssignmentBox: setuphandlers')
from Products.ECAssignmentBox.config import PROJECTNAME
from Products.ECAssignmentBox.config import DEPENDENCIES
import os
from Products.CMFCore.utils import getToolByName
import transaction
##code-section HEAD
##/code-section HEAD

def isNotECAssignmentBoxProfile(context):
    return context.readDataFile("ECAssignmentBox_marker.txt") is None

def setupHideToolsFromNavigation(context):
    """hide tools"""
    if isNotECAssignmentBoxProfile(context): return 
    # uncatalog tools
    site = context.getSite()
    toolnames = ['portal_ecabtool']
    portalProperties = getToolByName(site, 'portal_properties')
    navtreeProperties = getattr(portalProperties, 'navtree_properties')
    if navtreeProperties.hasProperty('idsNotToList'):
        for toolname in toolnames:
            try:
                portal[toolname].unindexObject()
            except:
                pass
            current = list(navtreeProperties.getProperty('idsNotToList') or [])
            if toolname not in current:
                current.append(toolname)
                kwargs = {'idsNotToList': current}
                navtreeProperties.manage_changeProperties(**kwargs)

def fixTools(context):
    """do post-processing on auto-installed tool instances"""
    if isNotECAssignmentBoxProfile(context): return 
    site = context.getSite()
    tool_ids=['portal_ecabtool']
    for tool_id in tool_ids:
	    if hasattr(site, tool_id):
	        tool=site[tool_id]
	        tool.initializeArchetype()



def updateRoleMappings(context):
    """after workflow changed update the roles mapping. this is like pressing
    the button 'Update Security Setting' and portal_workflow"""
    if isNotECAssignmentBoxProfile(context): return 
    wft = getToolByName(context.getSite(), 'portal_workflow')
    wft.updateRoleMappings()


def postInstall(context):
    """Called as at the end of the setup process. """
    # the right place for your custom code
    if isNotECAssignmentBoxProfile(context): return 
    site = context.getSite()


##code-section FOOT
##/code-section FOOT
