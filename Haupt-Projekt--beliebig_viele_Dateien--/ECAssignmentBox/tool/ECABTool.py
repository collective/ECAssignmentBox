# -*- coding: utf-8 -*-
# $Id: ECABTool.py 1599 2011-10-07 12:16:45Z amelung $
#
# Copyright (c) 2006-2011 Otto-von-Guericke-UniversitŠt Magdeburg
#
# This file is part of ECAssignmentBox.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'

#import sys
#import traceback
import cgi
import urllib

from string import join, split
from socket import getfqdn, gethostname
from urlparse import urlsplit, urlunsplit

from email.MIMEText import MIMEText 
from email.Header import Header

from zope.interface import implements
from ZODB.POSException import ConflictError
from Products.CMFCore.utils import getToolByName

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import Schema, BaseSchema, BaseContent, DisplayList, registerType 
#from Products.Archetypes.utils import shasattr

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.CMFCore.utils import UniqueObject
from Products.DCWorkflow.Transitions import TRIGGER_USER_ACTION

#from zLOG import LOG, INFO, ERROR
from Products.ECAssignmentBox.tool.Statistics import Statistics
from Products.ECAssignmentBox.tool.interfaces import IECABTool
from Products.ECAssignmentBox import config
from Products.ECAssignmentBox import LOG

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

    #security.declarePublic('getWfStatesDisplayList')
    def getWfStatesDisplayList(self, wfName=config.ECA_WORKFLOW_ID):
        """
        @return a DisplayList containing all state keys and state titles in 
                assignment's workflow
        """
        #LOG.info('xxx: getWfStatesDisplayList')
        
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
        
        #LOG.info('format: %s' % format)
        #LOG.info('value: %s' % value)
        
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
        #LOG.debug('Here we are in ECABTool#getFullNameById')
    
        mtool = self.portal_membership
        member = mtool.getMemberById(id)
        error = False

        if not member:
            return id

        try:
            sn        = member.getProperty('sn', None)
            givenName = member.getProperty('givenName', None)

        except:
            error = True
            
        #LOG.info('xdebug: sn, givenName: %s, %s' % (type(sn), type(givenName)))
        #LOG.info('xdebug: sn, givenName: %s, %s' % (sn, givenName))

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
        
        #LOG.info('xdebug: %s, %s, %s' % (userId, property, fallback, ))
        
        membership = getToolByName(self, 'portal_membership')
        member = membership.getMemberById(userId)
        
        try:
            return member.getProperty(property, fallback)
        except:
            return fallback
    
    
    #security.declarePublic('testAssignmentBoxType')
    def testAssignmentBoxType(self, item=None):
        """
        Returns True if item has an attribut 'isAssignmentBoxType' or - in case
        item is a catalog brain- index 'isAssignmentBoxType' is True
        """
        
        #LOG.debug('Here we are in ECABTool#testAssignmentBoxType: %s' % item)
        
        result = None
        
        if (item and hasattr(item, 'isAssignmentBoxType')):
            result = item.isAssignmentBoxType
            
            # dirty hack
            if repr(result) == 'Missing.Value': 
                result = False

        else:
            result = False
        
        #LOG.info('result: %s' % repr(result))
        
        return result

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
        #    LOG.warn("calculateMean: %s: %s" % (sys.exc_info()[0], e))
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
        #    LOG.warn("calculateMedian: %s: %s" % (sys.exc_info()[0], e))
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
        #plone_utils = getToolByName(self, 'plone_utils')

        portal      = portal_url.getPortalObject()
        fromAddress = portal.getProperty('email_from_address', None)

        #mailHost    = plone_utils.getMailHost()
        #charset     = plone_utils.getSiteEncoding()
        mailHost = getToolByName(portal, 'MailHost') #self.MailHost
        charset = portal.getProperty('email_charset', 'UTF-8')


        if fromAddress is None:
            LOG.error('Cannot send email: address or name is %s' % fromAddress)
            return

        try:
            if (type(text) == unicode):
                msg = MIMEText(text.encode(charset), 'plain', charset)
            else:
                msg = MIMEText(text, 'plain', charset)
        except Exception, e:
            LOG.error('Cannot send notification email: %s' % e)
            return

        try:
            if (type(subject) == unicode):
                subjHeader = Header(subject.encode(charset), charset)  
            else:
                subjHeader = Header(subject, charset)
        except Exception, e:
            LOG.error('Cannot send notification email: %s' % e)
            return

        msg['Subject'] = subjHeader
        msg['From'] = fromAddress
        msg['Subject'] = subject

        # This is a hack to suppress deprecation messages about send()
        # in SecureMailHost; the proposed alternative, secureSend(),
        # sucks.
        mailHost._v_send = 1
        
        for address in addresses:
            if address:
                try:
                    LOG.info("Sending email to %r" % address)

                    msg['To'] = address
                    
                    mailHost.send(msg.as_string())
                    
                except ConflictError, ce:
                    LOG.error('Failed sending email: %s' % ce)
                    raise
                except Exception, e:
                    LOG.error('Failed sending email from %s to %s' % 
                              (fromAddress, address))
                    LOG.error("Reason: %s: %r" % (e.__class__.__name__, str(e)))
            # end if
        # end for


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
