## Script (Python) "getFinalStateValues"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from Products.CMFCore.utils import getToolByName

I18N_DOMAIN = 'eduComponents'

REQUEST  = container.REQUEST
RESPONSE = REQUEST.RESPONSE

result = [0,0,0]

if hasattr(context, 'completedStates'):
    acc_states = context.getCompletedStates()
else:
    acc_states = ('accepted', 'graded', )

review_states = acc_states[:] + ('rejected', )
    
# get the portal's catalog
catalog = getToolByName(context, 'portal_catalog')

# get all items inside this ecfolder
brains = catalog.searchResults(path = {'query':'/'.join(context.getPhysicalPath()),  'depth':100,  }, 
                               #sort_on = 'getObjPositionInParent', 
                               review_state = review_states,
                               meta_type = ('ECAssignment', 'ECAutoAssignment', ),
                               )

result[0] = len(brains)

for brain in brains:
    if brain.review_state in acc_states:
        result[1] = result[1] + 1
    # Only elements not in acc_states will match here (rejected)
    elif brain.review_state in review_states:
        result[2] = result[2] + 1

return result

#status = 'failure'
#message = context.translate('Please select one or more items.')
#return state.set(status=status, portal_status_message = message)