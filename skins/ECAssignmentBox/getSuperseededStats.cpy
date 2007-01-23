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

# [total superseeded, total ECAssignmentBoxes, (1, #), (2, #), ..., (n, #)]
result = [0,0,]
resultWithDuplicates = []

# get the portal's catalog
catalog = getToolByName(context, 'portal_catalog')

# get the amount of ECAssignmentBoxes
brains = catalog.searchResults(path = {'query':'/'.join(context.getPhysicalPath()),  'depth':100,  }, 
                               meta_type = ('ECAssignmentBox', 'ECAutoAssignmentBox', ),
                               )
result[1] = len(brains)

# get all ECAssignments inside this ECFolder
brains = catalog.searchResults(path = {'query':'/'.join(context.getPhysicalPath()),  'depth':100,  }, 
                               sort_on = 'Creator', 
                               meta_type = ('ECAssignment', 'ECAutoAssignment', ),
                               )

result[0] = len(brains)

if len(brains) > 0:
    lastCreator = ""
    currAmount = 0
    
    for brain in brains:
        if not lastCreator:
            lastCreator = brain.Creator
        if brain.Creator == lastCreator:
            currAmount = currAmount + 1
        else:
            resultWithDuplicates.append(currAmount)
            lastCreator = brain.Creator
            currAmount = 1
    resultWithDuplicates.append(currAmount)
    resultWithDuplicates.sort()
    
    while len(resultWithDuplicates) > 0:
        last = resultWithDuplicates[0]
        result.append((last, resultWithDuplicates.count(last)))
        while resultWithDuplicates.count(last) > 0:
            resultWithDuplicates.remove(last)

return result

#status = 'failure'
#message = context.translate('Please select one or more items.')
#return state.set(status=status, portal_status_message = message)