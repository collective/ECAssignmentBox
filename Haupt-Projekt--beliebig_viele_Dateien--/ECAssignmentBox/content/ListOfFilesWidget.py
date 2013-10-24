from Products.Archetypes.Widget import FileWidget
from Products.Archetypes.Registry import registerWidget
from StringIO import StringIO
from AccessControl import ClassSecurityInfo

from Products.Archetypes.log import log


__author__ = """Tim Sabsch <t.sabsch@arcor.de>"""
__docformat__ = 'plaintext'

class ListOfFilesWidget(FileWidget):

    _properties = FileWidget._properties.copy()

    _properties.update({
        'macro' : "list_of_files_widget",
    })
    
    security = ClassSecurityInfo()
    
    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):
        """form processing that deals with binary data"""
        
        id = instance.getId()
        old_submission = instance.getSubmission()
        
        answer = form.get('answer' , empty_marker)
        file = form.get('file', empty_marker)
        
        submission = []
        filenames = []
        
        for index in xrange(len(file)):
            if getattr(file[index], 'filename') == '':
                #FileUpload instance is empty
                if answer[index] == '':
                    #text area is empty too -> keep old file
                    submission.append(old_submission[index])
                    filename = old_submission[index].getFilename()    
                else:
                    submission.append(StringIO(answer[index]))
                    filename = '%s_%s.txt' % (id, index+1)
            else:
                submission.append(file[index])
                filename = '%s_%s' % (id, getattr(file[index], 'filename'))
            
            filenames.append(filename)
            
        kwargs = {}
        kwargs['filenames'] = filenames
        
        return submission, kwargs

__all__ = ('ListOfFilesWidget')
    
registerWidget(ListOfFilesWidget,
               title='List of files',
               description=('A list of an undefined number of files'),
               used_for=('Products.ECAssignmentBox.content.ListOfFilesField',)
               )

