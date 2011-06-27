## Script (Python) "assignment_add"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=answer='', file='', msg=''
##title=Create a file for an assignment submission.
##
from DateTime import DateTime
from StringIO import StringIO

# resourcestrings
I18N_DOMAIN = 'eduComponents'

REQUEST  = container.REQUEST
RESPONSE = REQUEST.RESPONSE

# set default target action (e.g. in case of an error)
# target_action = context.getTypeInfo().getActionById('view')
target_action = context.getTypeInfo().getActionInfo(['object/view'])['url']


# remember the context type
contextType = context.meta_type

if not file:
    # no file uploaded, lets try to read the text field (answer)
    if len(answer) != 0:
        file = StringIO(answer)
    else:
        # neither file nor answer available
        msg = context.translate(\
          msgid   = 'file_read_error',
          domain  = I18N_DOMAIN,
          default = 'Neither answer nor uploaded file found.')

        #return state.set(status = 'failure', portal_status_message = msg)
        context.plone_utils.addPortalMessage(msg)
        return state.set(status = 'failure')

# get current date and time
now = DateTime()
# get current user's id
#user_id = REQUEST.get('AUTHENTICATED_USER', 'unknown')
user_id = context.portal_membership.getAuthenticatedMember().getId() 
# generate unique Id for this submission
id = str(user_id) + '.' + now.strftime('%Y%m%d') + '.' + now.strftime('%H%M%S')

# create assignment object
context.invokeFactory(id=id, type_name=context.allowed_content_types[0])
assignment = getattr(context, id)

# construct filename
if hasattr(file, 'filename'):
    filename = '%s_%s' % (id, file.filename)
else:
    # TOOD: get MIME-type and add extension
    filename = '%s.txt' % (id,)

# set file
# HINT: If file is instance of FileUpload, filename will be ignored. 
#       See Archetypes/Field.py in FileField._process_input.
assignment.setFile(file, filename=filename)
    
# evaluate this submission (actually implemented in ECAAB)
result = assignment.evaluate(context)

if result:
    if result[0]:
        # The submission was evaluated.
        msg = context.translate(
            msgid   = 'submission_saved',
            domain  = I18N_DOMAIN,
            default = 'Your submission has been saved.')
    
        # add possible message from evaluate
        msg += ' ' + result[1]
    
    else:
        msg = result
    
#target_action = '%s/%s' % (assignment.getId(), assignment.getTypeInfo().getActionInfo(['object/view'])['url'])

context.plone_utils.addPortalMessage(msg)
RESPONSE.redirect('%s/%s' % (context.absolute_url(), assignment.getId()))

