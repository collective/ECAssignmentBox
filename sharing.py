from zope.interface import implements
from plone.app.workflow.interfaces import ISharingPageRole
from plone.app.workflow import permissions

from Products.CMFPlone import PloneMessageFactory as _

class ECAssignmentResultGraderRole(object):
    implements(ISharingPageRole)
    
    title = _(u"title_ecab_can_grade", default=u"Can grade")
    required_permission = permissions.DelegateRoles

class ECQuizResultViewerRole(object):
    implements(ISharingPageRole)
    
    title = _(u"title_ecab_can_view_results", default=u"Can view results")
    required_permission = permissions.DelegateRoles
