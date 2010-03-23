# -*- coding: utf-8 -*-
# $Id: sharing.py 1297 2009-09-27 18:29:20Z amelung $
#
# Copyright (c) 2006-2009 Otto-von-Guericke University Magdeburg
#
# This file is part of ECAssignmentBox.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'
__version__   = '$Revision: 1.2 $'

from zope.interface import implements
from plone.app.workflow.interfaces import ISharingPageRole
from plone.app.workflow import permissions

from Products.CMFPlone import PloneMessageFactory as _

class ECAssignmentGraderRole(object):
    implements(ISharingPageRole)
    
    title = _(u"title_ecab_can_grade_assignments", default=u"Can grade assignments")
    required_permission = permissions.DelegateRoles

class ECAssignmentViewerRole(object):
    implements(ISharingPageRole)
    
    title = _(u"title_ecab_can_view_assignments", default=u"Can view assignments")
    required_permission = permissions.DelegateRoles
