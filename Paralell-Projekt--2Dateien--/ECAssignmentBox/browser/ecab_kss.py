from urlparse import urlsplit

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.interfaces import IAfterTransitionEvent
from kss.core import kssaction, KSSExplicitError
from kss.core.interfaces import IKSSView
from plone.app.kss.interfaces import IPloneKSSView
from plone.app.kss.plonekssview import PloneKSSView
from plone.app.layout.globals.interfaces import IViewView
from plone.locking.interfaces import ILockable
from zope.component import adapter
from zope.interface import implements

from Products.ECAssignmentBox.content.interfaces import IECAssignment


#@adapter(IECAssignment, IKSSView, IAfterTransitionEvent)
#def ecab_workflow_changed(obj, view, event):
#    """
#    """
#    if not (event.old_state == event.new_state):
#        viewletReloader = ViewletReloader(view)
#        viewletReloader.update_ecab_viewlets()
#
#
#class ViewletReloader(object):
#    """Reload viewlets that depend on the workflow state.
#    """
#
#    def __init__(self, view):
#        self.view = view
#        self.context = view.context
#        self.request = view.request
#
#    def update_ecab_viewlets(self):
#        """Refresh ECAB viewlets.
#        """
#        if IECAssignment.providedBy(self.context):
#            # only do this if the context is actually an ECAssignment.
#            zope = self.view.getCommandSet('zope')
#            zope.refreshViewlet('plone.belowcontentbody')


class WorkflowGadget(PloneKSSView):

    implements(IPloneKSSView, IViewView)

    @kssaction
    def ecabChangeWorkflowState(self, uid, url):
        """Change the workflow state, currently only of a ECAssignment."""
        context = aq_inner(self.context)
        ksscore = self.getCommandSet('core')
        zopecommands = self.getCommandSet('zope')
        plonecommands = self.getCommandSet('plone')

        locking = ILockable(context, None)
        if locking is not None and not locking.can_safely_unlock():
            selector = ksscore.getHtmlIdSelector('plone-lock-status')
            zopecommands.refreshViewlet(selector, 'plone.abovecontent',
                                        'plone.lockinfo')
            plonecommands.refreshContentMenu()
            return self.render()

        (proto, host, path, query, anchor) = urlsplit(url)
        if not path.endswith('content_status_modify'):
            raise KSSExplicitError('only content_status_modify is handled')
        action = query.split("workflow_action=")[-1].split('&')[0]
        uid_catalog = getToolByName(context, 'uid_catalog')
        brain = uid_catalog(UID=uid)[0]
        obj = brain.getObject()
        obj.content_status_modify(action)
        
        if IECAssignment.providedBy(self.context):
            # Only refresh content if the context is an ECAssignmentBox,
            # otherwise you get too much assignments listed.
            selector = ksscore.getCssSelector('.contentViews')
            zopecommands.refreshViewlet(selector, 'plone.contentviews',
                                        'plone.contentviews')
            zopecommands.refreshProvider('.tasklist_table',
                                         'xm.tasklist.simple')
            plonecommands.refreshContentMenu()
        else:
            # In all other cases, we can at least refresh the part
            # that shows the workflow info for this item.
            wf_change = obj.restrictedTraverse('ecab_workflow_change')
            html = wf_change()
            selector = ksscore.getHtmlIdSelector('id-%s' % uid)
            ksscore.replaceHTML(selector, html)
        
        self.issueAllPortalMessages()
        self.cancelRedirect()
