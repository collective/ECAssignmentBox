from cStringIO import StringIO
from logging import ERROR
from types import ClassType, FileType, StringType, UnicodeType

from zope.contenttype import guess_content_type
from zope.i18n import translate
from zope.i18nmessageid import Message
from zope import schema
from zope import component
from zope.interface import implements

from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from Acquisition import aq_base
from Acquisition import aq_get
from Acquisition import aq_parent
from Acquisition import aq_inner
from ComputedAttribute import ComputedAttribute
from DateTime import DateTime
from DateTime.DateTime import safelocaltime
from DateTime.interfaces import DateTimeError
from ExtensionClass import Base
from OFS.Image import File
from OFS.Image import Pdata
from OFS.Image import Image as BaseImage
from ZPublisher.HTTPRequest import FileUpload
from ZODB.POSException import ConflictError

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _getAuthenticatedUser
from Products.CMFCore import permissions

from Products.Archetypes import PloneMessageFactory as _
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.Layer import DefaultLayerContainer
from Products.Archetypes.interfaces.storage import IStorage
from Products.Archetypes.interfaces.base import IBaseUnit
from Products.Archetypes.interfaces.field import IField
from Products.Archetypes.interfaces.field import IObjectField
from Products.Archetypes.interfaces.field import IStringField
from Products.Archetypes.interfaces.field import ITextField
from Products.Archetypes.interfaces.field import IDateTimeField
from Products.Archetypes.interfaces.field import ILinesField
from Products.Archetypes.interfaces.field import IIntegerField
from Products.Archetypes.interfaces.field import IFloatField
from Products.Archetypes.interfaces.field import IFileField
from Products.Archetypes.interfaces.field import IImageField
from Products.Archetypes.interfaces.field import IFixedPointField
from Products.Archetypes.interfaces.field import IReferenceField
from Products.Archetypes.interfaces.field import IComputedField
from Products.Archetypes.interfaces.field import IBooleanField
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.Archetypes.interfaces import IVocabulary
from Products.Archetypes.exceptions import ObjectFieldException
from Products.Archetypes.exceptions import TextFieldException
from Products.Archetypes.exceptions import FileFieldException
from Products.Archetypes.exceptions import ReferenceException
from Products.Archetypes.Widget import BooleanWidget
from Products.Archetypes.Widget import CalendarWidget
from Products.Archetypes.Widget import ComputedWidget
from Products.Archetypes.Widget import DecimalWidget
from Products.Archetypes.Widget import FileWidget
from Products.Archetypes.Widget import ImageWidget
from Products.Archetypes.Widget import IntegerWidget
from Products.Archetypes.Widget import LinesWidget
from Products.Archetypes.Widget import StringWidget
from Products.Archetypes.Widget import ReferenceWidget
from Products.Archetypes.BaseUnit import BaseUnit
from Products.Archetypes.ReferenceEngine import Reference
from Products.Archetypes.log import log
from Products.Archetypes.utils import className
from Products.Archetypes.utils import mapply
from Products.Archetypes.utils import shasattr
from Products.Archetypes.utils import contentDispositionHeader
from Products.Archetypes.mimetype_utils import getAllowedContentTypes as getAllowedContentTypesProperty
from Products.Archetypes import config
from Products.Archetypes.Storage import AttributeStorage
from Products.Archetypes.Storage import ObjectManagedStorage
from Products.Archetypes.Storage import ReadOnlyStorage
from Products.Archetypes.Registry import setSecurity
from Products.Archetypes.Registry import registerField
from Products.Archetypes.Registry import registerPropertyType

from Products.validation import ValidationChain
from Products.validation import UnknowValidatorError
from Products.validation import FalseValidatorError
from Products.validation.interfaces.IValidator import IValidator, IValidationChain

from Products.Archetypes.interfaces import IFieldDefaultProvider

from plone.uuid.interfaces import IUUID

from Products.Archetypes.Field import ObjectField, FileField, registerField
from Products.ECAssignmentBox.content.ListOfFilesWidget import ListOfFilesWidget
from zExceptions import NotFound


# Import conditionally, so we don't introduce a hard depdendency
try:
    from plone.i18n.normalizer.interfaces import IUserPreferredFileNameNormalizer
    FILE_NORMALIZER = True
except ImportError:
    FILE_NORMALIZER = False
    

__author__ = """Tim Sabsch <t.sabsch@arcor.de>"""
__docformat__ = 'plaintext'


class MyFile(File):
    
    security = ClassSecurityInfo()
    
    security.declarePublic('getFilename')    
    def getFilename(self):
        return self.filename
    
    security.declarePublic('getContentType')
    def getContentType(self):
        return File.getContentType(self)
    
    security.declarePublic('getSize')
    def getSize(self):
        return File.get_size(self)
    
    security.declarePublic('getBestIcon')
    def getBestIcon(self):
        mtr = getToolByName(self, 'mimetypes_registry', None)
        # log("self.getIcon() in getBestIcon: %s" % self.getIcon())
        if mtr is None:
            return self.getIcon()
        try:
            lookup = mtr.lookup(self.getContentType())
            # log("self.getContentType in getBestIcon: %s" % self.getContentType())
            # log("lookup in getBestIcon: %s" % lookup)
        except MimeTypeException:
            return None
        
        if lookup:
            mti = lookup[0]
            # log("mti in getBestIcon: %s" % mti)
            #try:
                # this will get the following error: 
                # TypeError: 'MyFile' object has no attribute '__getitem__'
                # without this function call it works...
                # self.restrictedTraverse(mti.icon_path)
            return mti.icon_path
            #except (NotFound, KeyError, AttributeError):
               # pass
               
        return self.getIcon()


class ListOfFilesField(ObjectField):
    """any comment"""
    
    implements(IFileField, ILayerContainer)

    _properties = ObjectField._properties.copy()
    _properties.update({
        'type': 'list',
        'default': [],
        'primary': False,
        'widget': ListOfFilesWidget,
        'content_class': MyFile,
        'default_content_type': 'application/octet-stream',
    })

    security = ClassSecurityInfo()
        
              
    security.declarePrivate('get')
    def get(self, instance, **kwargs):
        list = ObjectField.get(self, instance, **kwargs)
        valuelist = []
        
        for value in list:
            if value and not isinstance(value, self.content_class):
                value = self._wrapValue(instance, value)
            valuelist.append(value)
        return valuelist
    
    
    security.declarePrivate('set')
    def set(self, instance, values, **kwargs): # check
        __traceback_info__ = (self.getName(), instance, values, kwargs)        

        # log("instance in set: %s" % instance)
        # log("values in set: %s" % values) 
        # log("filenames in set: %s" % kwargs.get('filenames', ''))   
        
        valuelist = []
        for index in xrange(len(values)):
            value = values[index]
            if value and not isinstance(value, self.content_class):
                #value != MyFile instance -> create one
                filename = kwargs.get('filenames', None)[index]
                if not filename:
                    filename = ''
                
                mimetype, enc = guess_content_type(filename, value)         
                value = self._wrapValue(instance, value, filename = filename, mimetype = mimetype)
                
            valuelist.append(value)  

        ObjectField.set(self, instance, valuelist)   
    
    
    security.declarePrivate('_wrapValue')
    def _wrapValue(self, instance, value, **kwargs):
        """Wraps the value in the content class if it's not wrapped
        """
        if isinstance(value, self.content_class):
            return value
        mimetype = kwargs.get('mimetype', self.default_content_type)
        filename = kwargs.get('filename', '')
        obj = self._make_file(self.getName(), title='',
                              file=value, instance=instance)
        setattr(obj, 'filename', filename)
        setattr(obj, 'content_type', mimetype)
        
        try:
            delattr(obj, 'title')
        except (KeyError, AttributeError):
            pass
              
        return obj
        
    
    security.declarePrivate('_make_file')    
    def _make_file(self, id, title='', file='', instance=None):
        """File content factory"""
        return self.content_class(id, title, file)      
        
    
    security.declareProtected(permissions.View, 'download')
    def download(self, instance, file, REQUEST=None, RESPONSE=None, no_output=False): # TODO
        """Kicks download.
        
        Writes data including file name and content type to RESPONSE
        """
        log("instance in download: %s" % instance)
        log("file in download und dict: %s, %s" % (file, file.__dict__))
        #list = self.get(instance, raw=True)
        #log("list in download: %s" % list)
        """
        if not REQUEST:
            REQUEST = aq_get(instance, 'REQUEST')
        if not RESPONSE:
            RESPONSE = REQUEST.RESPONSE
        file = list[0]
        filename = file.getFilename()
        #filename = self.getFilename(instance)
        if filename is not None:
            if FILE_NORMALIZER:
                filename = IUserPreferredFileNameNormalizer(REQUEST).normalize(
                    unicode(filename, instance.getCharset()))
            else:
                filename = unicode(filename, instance.getCharset())
            header_value = contentDispositionHeader(
                disposition='attachment',
                filename=filename)
            RESPONSE.setHeader("Content-Disposition", header_value)
        if no_output:
            return file
        
        return file.index_html(REQUEST, RESPONSE)   """
        
    def at_download(self):
        return 1
    
    
registerField(ListOfFilesField, 
              title='ListOfFilesField',
              description=('Used for storing a list of files'))