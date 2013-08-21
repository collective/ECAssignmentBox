# -*- coding: utf-8 -*-
# $Id: sharing.py 1570 2011-06-28 22:33:33Z amelung $
#
# Copyright (c) 2006-2011 Otto-von-Guericke-UniversitŠt Magdeburg
#
# This file is part of ECAssignmentBox.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'

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
