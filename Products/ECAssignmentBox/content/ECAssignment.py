# -*- coding: utf-8 -*-
# $Id$
#
# Copyright (c) 2006-2011 Otto-von-Guericke-UniversitŠt Magdeburg
#
# This file is part of ECAssignmentBox.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'

import re
import interfaces
from StringIO import StringIO
from textwrap import TextWrapper

from AccessControl import ClassSecurityInfo
from zope.interface import implements

from Products.Archetypes.atapi import Schema, BaseContent, registerType
from Products.Archetypes.atapi import FileField, TextField, StringField
from Products.Archetypes.atapi import FileWidget, RichWidget, StringWidget

#from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.content.schemata import ATContentTypeSchema, finalizeATCTSchema
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
#from Products.ATContentTypes.interfaces import IATDocument

# The following two imports are for getAsPlainText()
#from Products.ATContentTypes.content.base import translateMimetypeAlias
#from Products.PortalTransforms.utils import TransformException

from Products.ECAssignmentBox import config
from Products.ECAssignmentBox import LOG

# PlagDetector imports
from Products.ECAssignmentBox.PlagDetector.PlagChecker import PlagChecker
from Products.ECAssignmentBox.PlagDetector.PlagVisualizer import PlagVisualizer

#import logging
#log = logging.getLogger('ECAssignmentBox')

# alter default fields -> hide title and description
ECAssignmentSchema = ATContentTypeSchema.copy()
ECAssignmentSchema['id'].widget.visible = {
    'view' : 'invisible',
    'edit' : 'invisible'
}
ECAssignmentSchema['title'].default_method = '_generateTitle'
ECAssignmentSchema['title'].widget.visible = {
    'view' : 'invisible',
    'edit' : 'invisible'
}
ECAssignmentSchema['description'].widget.visible = {
    'view' : 'invisible',
    'edit' : 'invisible'
}

# define schema
ECAssignmentSchema = ECAssignmentSchema + Schema((
    FileField(
        'file',
        searchable = True,
        primary = True,
        widget = FileWidget(
            label = "Answer",
            label_msgid = "label_answer",
            description = "The submission for this assignment",
            description_msgid = "help_answer",
            i18n_domain = config.I18N_DOMAIN,
            macro = 'answer_widget',
        ),
    ),

    TextField(
        'remarks',
        allowable_content_types = config.ALLOWED_CONTENT_TYPES, 
        default_content_type = config.DEFAULT_CONTENT_TYPE, 
        default_output_type = config.DEFAULT_OUTPUT_TYPE,
        widget=RichWidget(
        #widget = TextAreaWidget(
            label = "Remarks",
            label_msgid = "label_remarks",
            description = "Your remarks for this assignment (they will not be shown to the student)",
            description_msgid = "help_remarks",
            i18n_domain = config.I18N_DOMAIN,
            rows = 7,
        ),
        read_permission = 'Modify Portal Content',
    ),

    TextField(
        'feedback',
        searchable = True,
        allowable_content_types = config.ALLOWED_CONTENT_TYPES, 
        default_content_type = config.DEFAULT_CONTENT_TYPE, 
        default_output_type = config.DEFAULT_OUTPUT_TYPE,
        widget=RichWidget(
        #widget = TextAreaWidget(
            label = "Feedback",
            label_msgid = "label_feedback",
            description = "The grader's feedback for this assignment",
            description_msgid = "help_feedback",
            i18n_domain = config.I18N_DOMAIN,
            rows = 7,
        ),
    ),

    StringField(
        'mark',
        #searchable = True,
        accessor = 'getGradeIfAllowed',
        edit_accessor = 'getGradeForEdit',
        mutator = 'setGrade',
        widget=StringWidget(
            label = 'Grade',
            label_msgid = 'label_grade',
            description = "The grade awarded for this assignment",
            description_msgid = "help_grade",
            i18n_domain = config.I18N_DOMAIN,
        ),
    ),
  ) # , marshall = PrimaryFieldMarshaller()
)

finalizeATCTSchema(ECAssignmentSchema)

class ECAssignment(BaseContent, HistoryAwareMixin):
    """A submission to an assignment box"""
    security = ClassSecurityInfo()

    implements(interfaces.IECAssignment)

    meta_type = 'ECAssignment'
    _at_rename_after_creation = True

    schema = ECAssignmentSchema

    ##code-section class-header #fill in your manual code here
    global_allow = False

    typeDescription = "A submission to an assignment box."
    typeDescMsgId = 'description_edit_eca'
    
    # work-around for indexing in a correct way
    isAssignmentBoxType = False
    isAssignmentType = True
    
    # Methods
    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
        """
        """
        BaseContent.manage_afterAdd(self, item, container)
        
        wtool = getToolByName(self, 'portal_workflow')
        assignments = self.contentValues(filter = {'Creator': item.Creator()})
        if assignments:
            for a in assignments:
                if a != self:
                    wf = wtool.getWorkflowsFor(a)[0]
                    if wf.isActionSupported(a, 'supersede'):
                        wtool.doActionFor(a, 'supersede',
                                          comment='Superseded by %s'
                                          % self.getId())

        self.sendNotificationEmail()
    
    
    security.declarePrivate('sendNotificationEmail')
    def sendNotificationEmail(self):
        """
        When this assignment is created, send a notification email to
        the owner of the assignment box, unless emailing is turned off.
        """
        #LOG.debug('Here we are in ECAssignmentBox#sendNotificationEmail')

        box = self.aq_parent
        
        # emailing is turned off by assignment box
        if not box.getSendNotificationEmail():
            return

        #portal_url = getToolByName(self, 'portal_url')
        #portal = portal_url.getPortalObject()

        site_properties = self.portal_properties.site_properties
        # 'en' is used as fallback language if default_language is not
        # set; this shouldn't normally happen

        ecab_utils = getToolByName(self, 'ecab_utils')

        portal_language = getattr(site_properties, 'default_language', 'en')
        portal_qi = getToolByName(self, 'portal_quickinstaller')
        productVersion = portal_qi.getProductVersion(config.PROJECTNAME)
        
        submitterId   = self.Creator()
        submitterName = ecab_utils.getFullNameById(submitterId)
        submissionURL = ecab_utils.normalizeURL(self.absolute_url())

        #addresses = box.getNotificationEmailAddresses()
        addresses = []
        addresses.append(ecab_utils.getUserPropertyById(box.Creator(), 'email'))
        prefLang = ecab_utils.getUserPropertyById(box.Creator(), 'language', portal_language)
        
        default_subject = '[${id}] Submission to "${box_title}" by ${student}'
        subject = self.translate(domain=config.I18N_DOMAIN,
                                 msgid='email_new_submission_subject',
                                 target_language=prefLang,
                                 mapping={'id': config.PROJECTNAME,
                                          'box_title': box.Title(),
                                          'student': submitterName},
                                 default=default_subject)

        default_mailText = '${student} has made a submission to ' \
                           'the assignment "${box_title}".\n\n' \
                           '<${url}>\n\n' \
                           '-- \n' \
                           '${product} ${version}'
        mailText = self.translate(domain=config.I18N_DOMAIN,
                                  msgid='email_new_submission_content',
                                  target_language=prefLang,
                                  mapping={'box_title': box.Title(),
                                           'student': submitterName,
                                           'url': submissionURL,
                                           'product': config.PROJECTNAME,
                                           'version': productVersion},
                                  default=default_mailText)

        LOG.info('Sending notification email to: %s' % addresses)
        ecab_utils.sendEmail(addresses, subject, mailText)

    #security.declarePrivate('sendGradingNotificationEmail')
    def sendGradingNotificationEmail(self):
        """
        When this assignment is graded, send a notification email to
        the submitter of the assignment, unless grading notification
        is turned off in the assignment box.
        """
        box = self.aq_parent
        if not box.getSendGradingNotificationEmail():
            return

        site_properties = self.portal_properties.site_properties
        ecab_utils = getToolByName(self, 'ecab_utils', None)

        # 'en' is used as fallback language if default_language is not
        # set; this shouldn't normally happen
        portal_language = getattr(site_properties, 'default_language', 'en')
        portal_qi = getToolByName(self, 'portal_quickinstaller')
        productVersion = portal_qi.getProductVersion(config.PROJECTNAME)
        
        submitterId   = self.Creator()
        #submitterName = ecab_utils.getFullNameById(submitterId)
        submissionURL = ecab_utils.normalizeURL(self.absolute_url())

        addresses = []
        addresses.append(ecab_utils.getUserPropertyById(submitterId, 'email'))
        
        prefLang = ecab_utils.getUserPropertyById(submitterId, 'language', portal_language)

        default_subject = 'Your submission to "${box_title}" has been graded'
        subject = self.translate(domain=config.I18N_DOMAIN,
                                 msgid='email_submission_graded_subject',
                                 target_language=prefLang,
                                 mapping={'box_title': box.Title(),},
                                 default=default_subject)

        default_mailText = 'Your submission to the assignment box ' \
                           '"${box_title}" has been graded.\n\n' \
                           'Visit the following URL to view your ' \
                           'submission:\n\n' \
                           '<${url}>\n\n' \
                           '-- \n' \
                           '${product} ${version}'
        mailText = self.translate(domain=config.I18N_DOMAIN,
                                  msgid='email_submission_graded_content',
                                  target_language=prefLang,
                                  mapping={'box_title': box.Title(),
                                           'grade': self.mark,
                                           'feedback': self.feedback,
                                           'url': submissionURL,
                                           'product': config.PROJECTNAME,
                                           'version': productVersion},
                                  default=default_mailText)

        LOG.info('Sending grading notification email to %s' % addresses)
        ecab_utils.sendEmail(addresses, subject, mailText)


    #security.declarePublic('setField')
    def setField(self, name, value, **kw):
        """
        FIXME: set security
        @deprecated: Why?
        Sets value of a field
        """
        field = self.getField(name)
        field.set(self, value, **kw)


    security.declarePrivate('_generateTitle')
    def _generateTitle(self):
        """
        """
        #LOG.info("xdebug: Title changed from '%s' to '%s'" % (self.title, self.getCreatorFullName(),))
        return self.getCreatorFullName()


    #security.declarePublic('getCreatorFullName')
    def getCreatorFullName(self):
        """
        FIXME: set security
        """
        ecab_utils = getToolByName(self, 'ecab_utils', None)

        if ecab_utils:
            return ecab_utils.getFullNameById(self.Creator())
        else:
            return self.Creator()

    #security.declarePublic('get_data')
    def get_data(self):
        """
        XXX:  EXPERIMENTAL
        
        If wrapAnswer is set for the box, plain text entered in the
        text area is stored as one line per paragraph. For display
        inside a <pre> element it should be wrapped.

        @return file content
        """
        result = None
        
        mt = self.getContentType('file')
        
        if re.match("(text/.+)|(application/(.+\+)?xml)", mt):
        
            box = self.aq_parent
            
            if (box.getWrapAnswer() and 
                ((mt == 'text/plain') or (mt == 'text/x-web-intelligent'))): 
                
                file = StringIO(self.getField('file').get(self))
                wrap = TextWrapper()
                result = ''
    
                for line in file:
                    result += wrap.fill(line) + '\n'
    
            else:
                result = str(self.getField('file').get(self))
        # end if

        # take care of hexadecimal Unicode escape sequences
        #if result: result = result.decode('unicode_escape')
        
        return result
    
    #security.declarePublic('getAsPlainText')
    def getAsPlainText(self):
        """
        FIXME: deprecated, use get_data or data in page templates
        
        Return the file contents as plain text.
        Cf. <http://www.bozzi.it/plone/>,
        <http://plone.org/Members/syt/PortalTransforms/user_manual>;
        see also portal_transforms in the ZMI for available
        transformations.
        
        @return file content as plain text or None
        """
        f = self.getField('file')
        mt = self.getContentType('file')
        
        if re.match('text/|application/(.+\+)?xml', mt):
            return str(f.get(self))
        else:
            return None
        
        """
        try:
            ptTool = getToolByName(self, 'portal_transforms')
            result = ptTool.convertTo('text/plain-pre', str(f.get(self)),
                                      mimetype=mt)
        except TransformException:
            result = None
            
        if result:
            return result.getData()
        else:
            return None
        """
    
    
    security.declarePublic('evaluate')
    def evaluate(self, parent, recheck=False):
        """
        Will be called if a new assignment is added to this assignment box to
        evaluate it. Please do not confuse this with the validation of the
        input values.
        For ECAssignment this mehtod returns nothing but it can be 
        overwritten in subclasses, e.g. ECAutoAssignmentBox.
        
        @return (1, '')
        """
        return (1, '')

    
    security.declarePublic('getGradeIfAllowed')
    def getGradeIfAllowed(self):
        """
        The accessor for field grade. Returns the grade if this assigment is in
        state graded or current user has reviewer permissions.
        
        @return string value of the given grade or nothing
        """
        wtool = getToolByName(self, 'portal_workflow')
        ecab_utils = getToolByName(self, 'ecab_utils')
        
        state = wtool.getInfoFor(self, 'review_state', '')
        
        currentUser = self.portal_membership.getAuthenticatedMember()
        #isReviewer = currentUser.checkPermission(permissions.ReviewPortalContent, self)
        #isOwner = currentUser.has_role(['Owner', 'Reviewer', 'Manager'], self)
        #isGrader = currentUser.has_role(['ECAssignment Grader', 'Manager'], self)
        #isGrader =  currentUser.checkPermission(permissions.GradeAssignments,self)
        isGrader = currentUser.checkPermission(config.GradeAssignments, self)

        if self.mark:
            try:
                value = self.mark
                prec = len(value) - value.find('.') - 1
                result = ecab_utils.localizeNumber("%.*f", (prec, float(value)))
            except ValueError:
                result = self.mark

            if state == 'graded':
                return result
            elif isGrader:
                return '(' + result + ')'


    security.declarePublic('getGradeDisplayValue')
    def getGradeDisplayValue(self):
        """
        Formats and returns the grade if given .
        
        @return string value of the given grade or nothing
        """
        wtool = self.portal_workflow
        ecab_utils = getToolByName(self, 'ecab_utils')

        state = wtool.getInfoFor(self, 'review_state', '')
        
        if self.mark:
            try:
                value = self.mark
                prec = len(value) - value.find('.') - 1
                result = ecab_utils.localizeNumber("%.*f", (prec, float(value)))
            except ValueError:
                result = self.mark

            if state == 'graded':
                return result
            else:
                return '(%s)' % result


    #security.declarePublic('getGradeForEdit')
    def getGradeForEdit(self):
        """
        The edit_accessor for field grade. Returns the grade for this
        assignment.
        
        @return string value of the given grade or nothing
        """
        
        try:
            value = self.mark
            prec = len(value) - value.find('.') - 1
            ecab_utils =  getToolByName(self, 'ecab_utils')
            
            return ecab_utils.localizeNumber("%.*f", (prec, float(value)))
        
        except ValueError:
            return self.mark


    security.declarePrivate('setGrade')
    def setGrade(self, value):
        """
        Mutator for the `mark' field.  Allows the input of localized numbers.
        """
        decimalSeparator = self.translate(msgid = 'decimal_separator',
                                          domain = config.I18N_DOMAIN,
                                          default = '.')
        value = value.strip()
        
        match = re.match('^[0-9]+' + decimalSeparator + '?[0-9]*$', value)
        if match:
            value = value.replace(decimalSeparator, '.')
        
        self.getField('mark').set(self, value)
    

    security.declarePublic('getViewerNames')
    def getViewerNames(self):
        """
        Get the names of the users and/or groups which have the local
        role `ECAssignment Viewer'.  This allows reviewers to quickly
        check who may view an assignment.
        
        @return list of user and/or group names
        """
        ecab_utils = getToolByName(self, 'ecab_utils')
        principalIds = self.users_with_local_role('ECAssignment Viewer')
        names = []
        
        for id in principalIds:
            if self.portal_groups.getGroupById(id):
                names.append(self.portal_groups.getGroupById(id).getGroupName())
            else:
                names.append(ecab_utils.getFullNameById(id))

        return names


    security.declarePublic('getGradeModeReadFieldNames')
    def getViewModeReadFieldNames(self):
        """
        Returns the names of the fields which are shown in view mode.
        This method should be overridden in subclasses which need more fields.

        @return list of field names
        """
        return ['file', 'remarks', 'feedback', 'mark']


    security.declarePublic('getGradeModeReadFieldNames')
    def getGradeModeReadFieldNames(self):
        """
        Returns the names of the fields which are read only in grade mode.
        This method should be overridden in subclasses which need more fields.

        @return list of field names
        """
        
        return ['file']


    security.declarePublic('getGradeModeEditFieldNames')
    def getGradeModeEditFieldNames(self):
        """
        Returns the names of the fields which are editable in grade mode.
        This method should be overridden in subclasses which need more fields.
        
        @return list of field names
        """
        return ['remarks', 'feedback', 'mark']


    security.declarePublic('getIndicators')
    def getIndicators(self):
        """
        Returns a list of dictionaries which contain information necessary
        to display the indicator icons.
        """
        result = []

        user = self.portal_membership.getAuthenticatedMember()
        isOwner = user.has_role(['Owner', 'Reviewer', 'Manager'], self);
        isGrader = self.portal_membership.checkPermission(config.GradeAssignments, self)        

        viewers = self.getViewerNames()
        
        if viewers:
            if isOwner:
                result.append({'icon':'ec_shared.png', 
                               'alt':'Released',
                               'alt_msgid':'label_released',
                               'title':'; '.join(viewers),
                               })
            elif user.has_role('ECAssignment Viewer', object=self):
                result.append({'icon':'ec_shared.png', 
                               'alt':'Released',
                               'alt_msgid':'label_released',
                               'title':'This assignment has been released for viewing',
                               'title_msgid':'tooltip_released_icon',
                               })
        
        if hasattr(self, 'feedback') and self.feedback:
            feedback = str(self.feedback)
            title = re.sub('[\r\n]+', ' ', feedback)

            result.append({'icon':'ec_comment.png', 
                           'alt':'Feedback',
                           'alt_msgid':'label_feedback',
                           'title':title,
                           })

        if isGrader and hasattr(self, 'remarks') and self.remarks:
            remarks = str(self.remarks)
            title = re.sub('[\r\n]+', ' ', remarks)

            result.append({'icon':'ecab_remarks.png', 
                           'alt':'Remarks',
                           'alt_msgid':'label_remarks',
                           'title':title,
                           })

        return result
        

    security.declarePublic('diff')
    def diff(self, other):
        """Compare this assignment to another one.
        """
        checker = PlagChecker()
        result = checker.compare(str(self.getFile()),
                        str(other.getFile()),
                        self.pretty_title_or_id(),
                        other.pretty_title_or_id())
        vis = PlagVisualizer()
        strList = vis.resultToHtml(result, 
                   str(self.getFile()),
                   str(other.getFile()))
        return strList


    security.declarePublic('diff2')
    def diff2(self, other):
        """Compare this assignment to another one.
        """
        checker = PlagChecker()
        result = checker.compare(str(self.getFile()),
                        str(other.getFile()),
                        self.pretty_title_or_id(),
                        other.pretty_title_or_id())
        vis = PlagVisualizer()
        strList = vis.resultToHtml(result, 
                   str(self.getFile()),
                   str(other.getFile()))
        return strList


    security.declarePublic('dotplot')
    def dotplot(self, other):#, REQUEST=None):
        """Compare this assignment to another one. Using a dotplot.
        """
        vis = PlagVisualizer()
        image = vis.stringsToDotplot(str(self.getFile()),
                             str(other.getFile()),
                             id1=self.pretty_title_or_id(),
                             id2=other.pretty_title_or_id(),
                             showIdNums=True)
        return image

 
    security.declarePublic('getLayout')
    def getLayout(self):
        """This exists to please the discussion form."""
        return 'eca_view'

 
registerType(ECAssignment, config.PROJECTNAME)
# end of class ECAssignment
