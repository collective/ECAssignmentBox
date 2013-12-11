from zope.contenttype import guess_content_type
from zExceptions import NotFound

from AccessControl import ClassSecurityInfo
from Acquisition import aq_get
from OFS.Image import File

from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions

from Products.Archetypes.log import log
from Products.Archetypes.utils import contentDispositionHeader
from Products.Archetypes.Registry import registerField

from Products.Archetypes.Field import ObjectField, FileField
from Products.ECAssignmentBox.content.ListWidget import ListWidget

try:
    from plone.i18n.normalizer.interfaces import IUserPreferredFileNameNormalizer
    FILE_NORMALIZER = True
except ImportError:
    FILE_NORMALIZER = False
    

__author__ = """Tim Sabsch <t.sabsch@arcor.de>"""
__docformat__ = 'plaintext'


class ListFile(File):
    
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
        
        if mtr is None:
            return self.getIcon()
        try:
            lookup = mtr.lookup(self.getContentType())

        except MimeTypeException:
            return None
        
        if lookup:
            mti = lookup[0]

            #try:
                # this will get the following error: 
                # TypeError: 'ListFile' object has no attribute '__getitem__'
                # without this function call it works...
                # self.restrictedTraverse(mti.icon_path)
            return mti.icon_path
            #except (NotFound, KeyError, AttributeError):
               # pass
               
        return self.getIcon()


class ListField(ObjectField):
    """A field that stores a list of files"""

    _properties = ObjectField._properties.copy()
    _properties.update({
        'type': 'list',
        'default': [],
        'primary': False,
        'widget': ListWidget,
        'content_class': ListFile,
        'default_content_type': 'application/octet-stream',
    })

    security = ClassSecurityInfo()
        
              
    security.declarePrivate('get')
    def get(self, instance, **kwargs):
        __traceback_info__ = (self.getName(), instance, kwargs)
        
        list = ObjectField.get(self, instance, **kwargs)
        valuelist = []
        
        for value in list:
            if value and not isinstance(value, self.content_class):
                value = self._wrapValue(instance, value)
            valuelist.append(value)
        return valuelist
    
    
    security.declarePrivate('set')
    def set(self, instance, values, **kwargs):
        
        valuelist = []
        for index in xrange(len(values)):
            value = values[index]
            if value and not isinstance(value, self.content_class):
                #value != ListFile instance -> create one
                filename = kwargs.get('filenames', None)[index]
                if not filename:
                    filename = ''
                
                mimetype, enc = guess_content_type(filename, value)         
                value = self._wrapValue(instance, value, filename = filename, mimetype = mimetype)
                
            valuelist.append(value)  

        ObjectField.set(self, instance, valuelist)   
    
    
    security.declarePrivate('_wrapValue')
    def _wrapValue(self, instance, value, **kwargs):
        
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
        return self.content_class(id, title, file)
    
    
    security.declareProtected(permissions.View, 'download')
    def download(self, instance, subpath, REQUEST=None, RESPONSE=None, no_output=False):
        # TODO: find a better method to identify the file
        
        __traceback_info__ = (self.getName(), instance, subpath)
        
        if not REQUEST:
            REQUEST = aq_get(instance, 'REQUEST')
        if not RESPONSE:
            RESPONSE = REQUEST.RESPONSE
        
        list = self.get(instance)
        file = None
        
        for value in list:
            if value.getFilename() == subpath:
                file = value
                break;
        if not file:
            raise NotFound
        
        filename = subpath
        
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
            return self

        return file.index_html(REQUEST, RESPONSE)        

    
registerField(ListField, 
              title='ListField',
              description=('Used for storing a list of files'))