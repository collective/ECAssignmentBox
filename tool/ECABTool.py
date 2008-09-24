# -*- coding: utf-8 -*-
# $Id: ECABTool.py,v 1.25 2008/05/15 16:41:35 amelung Exp $
#
# Copyright (c) 2006-2008 Otto-von-Guericke-Universität Magdeburg
#
# Generator: ArchGenXML Version 2.1
#            http://plone.org/products/archgenxml
#
# This file is part of ECAssignmentBox.
#
# GNU General Public License (GPL)
#

__author__ = """unknown <unknown>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces
from urlparse import *
from string import *
from socket import *

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
        """
        """
        BaseContent.__init__(self,'ecab_utils')
        self.setTitle('')
        
        ##code-section constructor-footer #fill in your manual code here
        ##/code-section constructor-footer


    # tool should not appear in portal_catalog
    def at_post_edit_script(self):
        """
        """
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

    #security.declarePublic('localizeNumber')
    def localizeNumber(self, format, value):
        """
        A simple method for localized formatting of decimal numbers,
        similar to locale.format().
        """

        result = format % value
        fields = result.split(".")
        decimalSeparator = self.translate(msgid = 'decimal_separator',
                                          domain = I18N_DOMAIN,
                                          default = '.')
        if len(fields) == 2:
            result = fields[0] + decimalSeparator + fields[1]
        elif len(fields) == 1:
            result = fields[0]
        else:
            raise ValueError, "Too many decimal points in result string"

        return result


    #security.declarePublic('getFullNameById')
    def getFullNameById(self, id):
        """
        Returns the full name of a user by the given ID. 
        """
        mtool = self.portal_membership
        member = mtool.getMemberById(id)
        error = False

        if not member:
            return id

        try:
            sn        = member.getProperty('sn')
            givenName = member.getProperty('givenName')
        except:
            error = True

        if error or (not sn) or (not givenName):
            fullname = member.getProperty('fullname', '')

            if fullname == '':
                return id

            if fullname.find(' ') == -1:
                return fullname

            sn = fullname[fullname.rfind(' ') + 1:]
            givenName = fullname[0:fullname.find(' ')]

        #log('xxx_sn: %s' % str(sn))
        #log('xxx_gn: %s' % str(givenName))

        return sn + ', ' + givenName


    #security.declarePublic('getUserPropertyById')
    def getUserPropertyById(self, id, property=''):
        """
        """
        mtool = self.portal_membership
        member = mtool.getMemberById(id)

        try:
            value = member.getProperty(property)
        except:
            return None

        return value


    #security.declarePublic('isAssignmentBoxType')
    def isAssignmentBoxType(self, item=None):
        """
        Returns True if item has a method 'isAssignmentBoxType' or - in case
        item is a ctalog brain- index 'isAssignmentBoxType' is True
        """
        
        if not item:
            return False
        else:
            return hasattr(item, 'isAssignmentBoxType') and item.isAssignmentBoxType

    def isGrader(self, item, id=None):
        """
        Returns True if the user given by id has permission to grade the
        assignment given by item; otherwise False.

        If id is None, the check will be done for the current user.

        @param item an assignment
        @param id a user id
        """
        mtool = self.portal_membership

        if not id:
            member = mtool.getAuthenticatedMember()
        else:
            member = mtool.getMemberById(id)

        return member.checkPermission(GradeAssignments, item)


    #security.declarePublic('getStatesToShow')
    def getStatesToShow(self, showSuperseded=False, state=None):
        """
        Returns a list of state names which will be used as a filter
        for showing assignments.
        """

        # FIXME: states are static names but they shoul better be taken from
        #        workflow_tool for the given object
        result = ('submitted', 'pending', 'accepted', 'rejected', 'graded',)

        if state is not None:
            if type(state) not in [tuple, list]:
                state = (state,)
            result = [s for s in state if s in result]

        if showSuperseded:
            result += ('superseded',)

        return result



    #security.declarePublic('findAssignments')
    def findAssignments(self, context, id):
        """
        """
        ct = getToolByName(self, 'portal_catalog')
        ntp = getToolByName(self, 'portal_properties').navtree_properties
        currentPath = None
        query = {}

        if context == self:
            currentPath = getToolByName(self, 'portal_url').getPortalPath()
            query['path'] = {'query':currentPath,
                             'depth':ntp.getProperty('sitemapDepth', 2)}
        else:
            currentPath = '/'.join(context.getPhysicalPath())
            query['path'] = {'query':currentPath, 'navtree':1}

        query['portal_type'] = ('ECAssignment',)
        #rawresult = ct(**query)
        rawresult = ct(path=currentPath, portal_type='ECAssignment',
                       Creator=id)
        return rawresult


    #security.declarePublic('calculateMean')
    def calculateMean(self, list):
        """
        """
        try:
            stats = Statistics(map((float), list))
        except:
            return None

        return stats.mean


    #security.declarePublic('calculateMedian')
    def calculateMedian(self, list):
        """
        """
        try:
                stats = Statistics(map((float), list))
        except:
                return None

        return stats.median

    def normalizeURL(self, url):
        """
        Takes a URL (as returned by absolute_url(), for example) and
        replaces the hostname with the actual, fully-qualified
        hostname.
        """
        url_parts = urlsplit(url)
        hostpart  = url_parts[1]
        port      = ''

        if hostpart.find(':') != -1:
            (hostname, port) = split(hostpart, ':')
        else:
            hostname = hostpart

        if hostname == 'localhost' or hostname == '127.0.0.1':
            hostname = getfqdn(gethostname())
        else:
            hostname = getfqdn(hostname)

        if port:
            hostpart = join((hostname, port), ':')

        url = urlunsplit((url_parts[0], hostpart, \
                          url_parts[2], url_parts[3], url_parts[4]))
        return url


    #security.declarePublic('urlencode')
    def urlencode(self, *args, **kwargs):
        return urllib.urlencode(*args, **kwargs)

    #security.declarePublic('parseQueryString')
    def parseQueryString(self, *args, **kwargs):
        return cgi.parse_qs(*args, **kwargs)


    #security.declarePrivate('sendEmail')
    def sendEmail(self, addresses, subject, text):
        """
        Send an e-mail message to the specified list of addresses.
        """

        if not addresses:
            return

        portal_url  = getToolByName(self, 'portal_url')
        plone_utils = getToolByName(self, 'plone_utils')

        portal      = portal_url.getPortalObject()
        mailHost    = plone_utils.getMailHost()
        charset     = plone_utils.getSiteEncoding()
        fromAddress = portal.getProperty('email_from_address', None)

        if fromAddress is None:
            log('Cannot send notification e-mail: E-mail sender address or name not set')
            return

        try:
            if (type(text) == unicode):
                message = MIMEText(text.encode(charset), 'plain', charset)
            else:
                message = MIMEText(text, 'plain', charset)
        except Exception, e:
            log_exc('Cannot send notification e-mail: %s' % e)
            return

        try:
            if (type(subject) == unicode):
                subjHeader = Header(subject.encode(charset), charset)  
            else:
                subjHeader = Header(subject, charset)
        except Exception, e:
            log_exc('Cannot send notification e-mail: %s' % e)
            return

        message['Subject'] = subjHeader

        # This is a hack to suppress deprecation messages about send()
        # in SecureMailHost; the proposed alternative, secureSend(),
        # sucks.
        mailHost._v_send = 1

        for address in addresses:
            try:
                mailHost.send(message = str(message),
                              mto = address,
                              mfrom = fromAddress,)
            except ConflictError, ce:
                log_exc('Cannot send notification e-mail: %s' % ce)
                raise
            except:
                log_exc('Could not send e-mail from %s to %s regarding submission to %s\ntext is:\n%s\n' % (fromAddress, address, self.absolute_url(), message,))


    def pathQuote(self, string=''):
        """
        Returns a string which is save to use as a filename.

        @param string some string
        """

        SPACE_REPLACER = '_'
        # Replace any character not in [a-zA-Z0-9_-] with SPACE_REPLACER
        ALLOWED_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-'
        ret = ''
        for c in string:
            if(c in ALLOWED_CHARS):
                ret += c
            else:
                ret += SPACE_REPLACER
        return ret


registerType(ECABTool, PROJECTNAME)
# end of class ECABTool

##code-section module-footer #fill in your manual code here
##/code-section module-footer



