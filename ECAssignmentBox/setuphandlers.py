# -*- coding: utf-8 -*-
# $Id: setuphandlers.py 1570 2011-06-28 22:33:33Z amelung $
#
# Copyright (c) 2006-2011 Otto-von-Guericke-UniversitŠt Magdeburg
#
# This file is part of ECAssignmentBox.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'

import transaction

from Products.CMFCore.utils import getToolByName

from Products.ECAssignmentBox import config
from Products.ECAssignmentBox import LOG

def isNotECAssignmentBoxProfile(context):
    """
    """
    return context.readDataFile("ECAssignmentBox_marker.txt") is None


def hideToolsFromNavigation(context):
    """Hide auto-installed tool instances from navigation
    """
    if isNotECAssignmentBoxProfile(context): return 
    
    # this tools will be uncataloged
    tool_id = 'ecab_utils'

    site = context.getSite()
    portal = getToolByName(site, 'portal_url').getPortalObject()

    portalProperties = getToolByName(site, 'portal_properties')
    navtreeProperties = getattr(portalProperties, 'navtree_properties')
    
    if navtreeProperties.hasProperty('idsNotToList'):
        # get IDs of all unlisted items
        current = list(navtreeProperties.getProperty('idsNotToList') or [])
        
        # add our tools to list of unlisted items
        if tool_id not in current:
            current.append(tool_id)
            kwargs = {'idsNotToList': current}
            navtreeProperties.manage_changeProperties(**kwargs)

        # unindex our tools        
        try:
            portal[tool_id].unindexObject()
        except:
            LOG.warn('Could not unindex object: %s' % tool_id)


def fixTools(context):
    """Do post-processing on auto-installed tool instances
    """
    if isNotECAssignmentBoxProfile(context): return 
    
    site = context.getSite()
    tool_id = 'ecab_utils'
    
    if hasattr(site, tool_id):
        tool = site[tool_id]
        tool.initializeArchetype()


def updateRoleMappings(context):
    """After workflow changed update the roles mapping.  This is like 
    pressing the button 'Update Security Setting' and portal_workflow
    """
    if isNotECAssignmentBoxProfile(context): return 
    wft = getToolByName(context.getSite(), 'portal_workflow')
    wft.updateRoleMappings()


def postInstall(context):
    """Called as at the end of the setup process. """
    # the right place for your custom code
    if isNotECAssignmentBoxProfile(context): return 

    reindexIndexes(context)


def installGSDependencies(context):
    """Install dependend profiles."""
    
    if isNotECAssignmentBoxProfile(context): return 
    
    # Has to be refactored as soon as generic setup allows a more 
    # flexible way to handle dependencies.
    return


def installQIDependencies(context):
    """Install dependencies"""
    if isNotECAssignmentBoxProfile(context): return 

    site = context.getSite()

    portal = getToolByName(site, 'portal_url').getPortalObject()
    quickinstaller = portal.portal_quickinstaller
    for dependency in config.DEPENDENCIES:
        if quickinstaller.isProductInstalled(dependency):
            LOG.info('Reinstalling dependency %s:' % dependency)
            quickinstaller.reinstallProducts([dependency])
            transaction.savepoint()
        else:
            LOG.info('Installing dependency %s:' % dependency)
            quickinstaller.installProduct(dependency)
            transaction.savepoint()


def reindexIndexes(context):
    """Reindex some indexes.

    Indexes that are added in the catalog.xml file get cleared
    everytime the GenericSetup profile is applied.  So we need to
    reindex them.

    Since we are forced to do that, we might as well make sure that
    these get reindexed in the correct order.
    """
    if isNotECAssignmentBoxProfile(context): return 

    site = context.getSite()

    pc = getToolByName(site, 'portal_catalog')
    indexes = [
        'isAssignmentBoxType',
        'isAssignmentType',
        'getRawAssignment_reference',
        'getRawRelatedItems',
        'review_state',
        ]

    # Don't reindex an index if it isn't actually in the catalog.
    # Should not happen, but cannot do any harm.
    ids = [id for id in indexes if id in pc.indexes()]
    if ids:
        pc.manage_reindexIndex(ids=ids)

    LOG.info('Indexes %s re-indexed.' % indexes)
