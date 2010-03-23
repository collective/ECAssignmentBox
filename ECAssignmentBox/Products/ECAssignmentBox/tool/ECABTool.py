# -*- coding: utf-8 -*-
# $Id: ECABTool.py 1330 2009-09-28 15:58:57Z amelung $
#
# Copyright (c) 2006-2009 Otto-von-Guericke University Magdeburg
#
# This file is part of ECAssignmentBox.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'
__version__   = '$Revision: 1.1 $'

#import sys
import cgi
import urllib
#import interfaces
from string import join, split
from socket import getfqdn, gethostname
from urlparse import urlsplit, urlunsplit

from email.MIMEText import MIMEText
from email.Header import Header

#from Globals import InitializeClass
from zope.interface import implements
from ZODB.POSException import ConflictError
from Products.CMFCore.utils import getToolByName

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import Schema, BaseSchema, BaseContent, \
    DisplayList, registerType 
from Products.Archetypes.utils import shasattr
#import sys
#import traceback

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.CMFCore.utils import UniqueObject
from Products.DCWorkflow.Transitions import TRIGGER_USER_ACTION


#from zLOG import LOG, INFO, ERROR
from Products.ECAssignmentBox.tool.Statistics import Statistics
from Products.ECAssignmentBox.tool.interfaces import IECABTool
from Products.ECAssignmentBox import config

import logging
log = logging.getLogger('ECAssignmentBox')

schema = Schema((
),
)

ECABTool_schema = BaseSchema.copy() + schema.copy()

class ECABTool(UniqueObject, BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(IECABTool)
    meta_type = 'ECABTool'
    plone_tool = True
    _at_rename_after_creation = True

    schema = ECABTool_schema

    def __init__(self, id=None):
        """
        Tool-constructors have no id argument, the id is fixed
        """
        BaseContent.__init__(self, 'ecab_utils')
        self.setTitle('')
        
    def at_post_edit_script(self):
        """
        Tool should not appear in portal_catalog
        """
        self.unindexObject()
        

    # -- Methods --------------------------------------------------------------
    #security.declarePrivate('getWfStates')
    def getWfStates(self, wfName=config.ECA_WORKFLOW_ID):
        """
        @return a list containing all state keys in assignment's workflow
        """
        wtool = self.portal_workflow
        return wtool.getWorkflowById(wfName).states.keys()

    #security.declarePrivate('getWfStatesDisplayList')
    def getWfStatesDisplayList(self, wfName=config.ECA_WORKFLOW_ID):
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

    #security.declarePrivate('getWfTransitions')
    def getWfTransitions(self, wfName=config.ECA_WORKFLOW_ID):
        """
        @return all transitions for the given workflow
        """
        
        result = {}
        
        wtool = self.portal_workflow
        wf = wtool.getWorkflowById(wfName)

        for tid in wf.transitions.keys():
            tdef = wf.transitions.get(tid, None)
            if tdef is not None and \
               tdef.trigger_type == TRIGGER_USER_ACTION and \
               tdef.actbox_name and \
               not result.has_key(tdef.id):
                result[tdef.id] = {
                        'id': tdef.id,
                        'title': tdef.title,
                        'title_or_id': tdef.title_or_id(),
                        'description': tdef.description,
                        'name': tdef.actbox_name}
        
        return tuple(result.values())


    #security.declarePrivate('getWfTransitionsDisplayList')
    def getWfTransitionsDisplayList(self, wfName=config.ECA_WORKFLOW_ID):
        """
        @return a DisplayList containing all transition keys and titles in 
                assignment's workflow
        """
        dl = DisplayList(())

        #wtool = self.portal_workflow
        #wf = wtool.getWorkflowById(wfName)

        for transition in self.getWfTransitions():
            # FIXME: not sure if this works with the result 
            # from getWfTransitions
            dl.add(transition.id, transition.actbox_name)

        return dl.sortedByValue()

    #security.declarePublic('localizeNumber')
    def localizeNumber(self, format, value):
        """
        A simple method for localized formatting of decimal numbers,
        similar to locale.format().
        """
        
        #log.info('format: %s' % format)
        #log.info('value: %s' % value)
        
        if not value: return None

        result = format % value
        fields = result.split(".")
        decimalSeparator = self.translate(msgid = 'decimal_separator',
                                          domain = config.I18N_DOMAIN,
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
        Returns the full name of a user by the given ID.  If full name is
        devided into given and last name, we return it in the format
        Doo, John; otherwise we will return 'fullname' as provided by Plone. 
        """
        #log.debug('Here we are in ECABTool#getFullNameById')
    
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
            else: 
                return fullname

            #if fullname.find(' ') == -1:
            #    return fullname
            #
            #sn = fullname[fullname.rfind(' ') + 1:]
            #givenName = fullname[0:fullname.find(' ')]
            
        else:
            #return sn + ', ' + givenName
            # print 'givenName, sn: %s, %s' % (givenName, sn, )
            return '%s, %s' % (sn, givenName)


    security.declarePublic('getUserPropertyById')
    def getUserPropertyById(self, userId, property, fallback=None):
        """
        @return: Value for 'property' or None
        """
        
        #log.debug('Here we are in ECABTool#getUserPropertyById')
        
        membership = getToolByName(self, 'portal_membership')
        member = membership.getMemberById(userId)

        try:
            value = member.getProperty(property)
        except:
            return fallback

        return value
    
    
    #security.declarePublic('testAssignmentBoxType')
    def testAssignmentBoxType(self, item=None):
        """
        Returns True if item has an attribut 'isAssignmentBoxType' or - in case
        item is a catalog brain- index 'isAssignmentBoxType' is True
        """
        
        #log.debug('Here we are in ECABTool#testAssignmentBoxType: %s' % item)
        
        if (item and shasattr(item, 'isAssignmentBoxType')):
            return item.isAssignmentBoxType
        else:
            return False

    #security.declarePublic('isGrader')
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

        return member.checkPermission(config.GradeAssignments, item)


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
        #except Exception, e:
        #    log.warn("calculateMean: %s: %s" % (sys.exc_info()[0], e))
        except:
            return None

        return stats.mean


    #security.declarePublic('calculateMedian')
    def calculateMedian(self, list):
        """
        """
        try:
            stats = Statistics(map((float), list))
        #except Exception, e:
        #    log.warn("calculateMedian: %s: %s" % (sys.exc_info()[0], e))
        except:
            return None

        return stats.median


    #security.declarePublic('normalizeURL')
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
        """
        """
        return urllib.urlencode(*args, **kwargs)


    #security.declarePublic('parseQueryString')
    def parseQueryString(self, *args, **kwargs):
        """
        """
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
            log.error('Cannot send email: address or name is %s' % fromAddress)
            return

        try:
            if (type(text) == unicode):
                message = MIMEText(text.encode(charset), 'plain', charset)
            else:
                message = MIMEText(text, 'plain', charset)
        except Exception, e:
            log.error('Cannot send notification email: %s' % e)
            return

        try:
            if (type(subject) == unicode):
                subjHeader = Header(subject.encode(charset), charset)  
            else:
                subjHeader = Header(subject, charset)
        except Exception, e:
            log.error('Cannot send notification email: %s' % e)
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
                log.error('Cannot send notification email: %s' % ce)
                raise
            except Exception, e:
                log.error('Could not send email from %s to %s: %s' % 
                          (fromAddress, address, e,))


    #security.declarePrivate('pathQuote')
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


registerType(ECABTool, config.PROJECTNAME)
