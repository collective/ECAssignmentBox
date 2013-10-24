# -*- coding: utf-8 -*-
# $Id: ecabsettings.py 1599 2011-10-07 12:16:45Z amelung $
#
# Copyright (c) 2006-2011 Otto-von-Guericke-UniversitŠt Magdeburg
#
# This file is part of ECAutoAssessmentBox.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'

#from Acquisition import aq_inner

from zope import event
from zope.app.component.hooks import getSite
from zope.component import adapts
from zope.formlib import form
from zope.interface import implements, Interface
#from zope.lifecycleevent import ObjectCreatedEvent
from zope.lifecycleevent import ObjectModifiedEvent
#from zope.schema import Text
from zope.schema import TextLine
from zope.schema import List
from zope.schema import Int
from zope.schema import Password
#from zope.schema import Tuple
#from zope.schema import Choice

from plone.app.controlpanel.form import ControlPanelForm
#from plone.app.form.validators import null_validator
from plone.fieldsets.fieldsets import FormFieldsets

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
#from Products.CMFPlone.PropertiesTool import SimpleItemWithProperties

from Products.ECAssignmentBox import ECMessageFactory as _
from Products.ECAssignmentBox import config
from Products.ECAssignmentBox import LOG

I18N_DOMAIN = 'eduComponents'

class IECABControlPanelSchema(Interface):
    """
    Spooler fieldset schema
    """

    student_id_attr = TextLine(
            title=_(u"label_student_id", default=u"Student ID"),
            description=_(u"help_student_id_attr",
                          default=u"The user attribute which stores the student ID."),
            default=u'student_id',
            required=True)

    major_attr = TextLine(
            title=_(u"label_major", default=u"Major"),
            description=_(u"help_major_attr",
                          default=u"The user attribute which stores a student's major."),
            default=u'major',
            required=True)

    personal_title_attr = TextLine(
            title=_(u"label_personal_title", default=u"Title"),
            description=_(u"help_personal_title_attr",
                          default=u"The user attribute which stores a student's personal title (such as &ldquo;Mr.&rdquo; or &ldquo;Ms.&rdquo;)."),
            default = u'personal_title',
            required = True)


class ECABControlPanelAdapter(SchemaAdapterBase):

    implements(IECABControlPanelSchema)
    adapts(IPloneSiteRoot)
    
    def __init__(self, context):
        super(ECABControlPanelAdapter, self).__init__(context)
        self.portal = getSite()
        pprop = getToolByName(self.portal, 'portal_properties')
        self.context = pprop.ecab_properties
        #self.encoding = pprop.site_properties.default_charset

    # base fieldset

    def get_student_id_attr(self):
        return self.context.student_id_attr

    def set_student_id_attr(self, value):
        self.context._updateProperty('student_id_attr', value)

    student_id_attr = property(get_student_id_attr, set_student_id_attr)

    def get_major_attr(self):
        return self.context.major_attr

    def set_major_attr(self, value):
        self.context._updateProperty('major_attr', value)

    major_attr = property(get_major_attr, set_major_attr)

    def get_personal_title_attr(self):
        return self.context.personal_title_attr

    def set_personal_title_attr(self, value):
        self.context._updateProperty('personal_title_attr', value)

    personal_title_attr = property(get_personal_title_attr, set_personal_title_attr)


main_set = FormFieldsets(IECABControlPanelSchema)
main_set.id = 'ecab_settings_spooler'
main_set.label = _(u"legend_ecab_attr_mapping", default=u"Student attributes mapping")
main_set.description =  _(u"help_ecab_attr_mapping", 
                          default=u"Here you can specify user attributes which "
                                   "should be used to retrieve additional student "
                                   "information.  The available user attributes are "
                                   "listed in portal_memberdata in the "
                                   "Zope Management Interface (ZMI).")
 
class ECABControlPanel(ControlPanelForm):
    """
    """
    
    form_fields = FormFieldsets(main_set, )

    label = _(u"heading_ecab_prefs", 
              default=u"Assignment Box Settings")
    
    description = _(u"description_ecspooler_setup",
                    default=u"Settings that affect the "
                             "behavior of all assignment boxes on this site.")
    
    form_name = _("ECAB settings")
