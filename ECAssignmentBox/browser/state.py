#import Acquisition
#from Products.Five import BrowserView
from zope.cachedescriptors.property import Lazy
#from plone.memoize.view import memoize_contextless

from Products.ECAssignmentBox.browser.ecabbase import ECABBaseView
#from Products.eXtremeManagement import interfaces

class WorkflowChangeView(ECABBaseView):

    @Lazy
    def transitions(self):
        return self.workflow.getTransitionsFor(self.context)

    @Lazy
    def review_state_id(self):
        return self.workflow.getInfoFor(self.context, 'review_state')

    @Lazy
    def review_state_title(self):
        return self.workflow.getTitleForStateOnType(
            self.review_state_id, self.context.portal_type)
