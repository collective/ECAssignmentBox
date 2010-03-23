# -*- coding: utf-8 -*-
# $Id: setuphandlers.py 1328 2009-09-28 15:54:07Z amelung $
#
# Copyright (c) 2006-2009 Otto-von-Guericke University Magdeburg
#
# This file is part of ECAssignmentBox.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'
__version__   = '$Revision: 1.2 $'

import transaction
import logging
log = logging.getLogger('ECAssignmentBox: setuphandlers')

from Products.ECAssignmentBox import config
from Products.CMFCore.utils import getToolByName


def isNotECAssignmentBoxProfile(context):
    """
    """
    return context.readDataFile("ECAssignmentBox_marker.txt") is None


def setupHideToolsFromNavigation(context):
    """hide tools"""
    if isNotECAssignmentBoxProfile(context): return 
    
    # uncatalog tools
    toolnames = ['ecab_utils']

    site = context.getSite()
    portal = getToolByName(site, 'portal_url').getPortalObject()

    portalProperties = getToolByName(site, 'portal_properties')
    navtreeProperties = getattr(portalProperties, 'navtree_properties')
    
    if navtreeProperties.hasProperty('idsNotToList'):
        current = list(navtreeProperties.getProperty('idsNotToList') or [])
        # add all ids 
        for toolname in toolnames:
            if toolname not in current:
                current.append(toolname)
                kwargs = {'idsNotToList': current}
                navtreeProperties.manage_changeProperties(**kwargs)

        for item in current:
            try:
                portal[item].unindexObject()
            except:
                log.warn('Could not unindex object: %s' % item)


def fixTools(context):
    """do post-processing on auto-installed tool instances"""
    if isNotECAssignmentBoxProfile(context): return 
    
    site = context.getSite()
    tool_ids=['ecab_utils']
    
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
            log.info('Reinstalling dependency %s:' % dependency)
            quickinstaller.reinstallProducts([dependency])
            transaction.savepoint()
        else:
            log.info('Installing dependency %s:' % dependency)
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

#    # uncatalog tools
#    portalProperties = getToolByName(site, 'portal_properties')
#    navtreeProperties = getattr(portalProperties, 'navtree_properties')
#
#    if navtreeProperties.hasProperty('idsNotToList'):
#        portal = getToolByName(site, 'portal_url').getPortalObject()
#        ids = list(navtreeProperties.getProperty('idsNotToList') or [])
#        for id in ids:
#            try:
#                portal[id].unindexObject()
#            except:
#                log.warn('Could not unindex object: %s' % id)
    
    log.info('Reindexed %s' % indexes)
