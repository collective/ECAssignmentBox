## Controller Python Script "assignments_cut"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Cut assignments and copy to the clipboard
##

# Borrowed from Plone's folder_cut.cpy

from OFS.CopySupport import CopyError

REQUEST=context.REQUEST

# paths
paths = []

# get all boxes
boxes = REQUEST.get('ecabox', [])

# get selected items
for box in boxes:
    paths.extend(REQUEST.get(box, []))

if paths:
    ids = [p.split('/')[-1] or p.split('/')[-2] for p in paths]

    try:
        context.manage_cutObjects(ids, REQUEST)
    except CopyError:
        message = context.translate("One or more items not moveable.")
        context.plone_utils.addPortalMessage(message)
        return state.set(status = 'failure')
    except AttributeError:
        message = context.translate("One or more selected items is no longer available.")
        context.plone_utils.addPortalMessage(message)
        return state.set(status = 'failure')

    from Products.CMFPlone.utils import transaction_note
    transaction_note('Cut %s from %s' % ((str(ids)), context.absolute_url()))

    #return state.set(portal_status_message='%s Item(s) cut.'%len(ids) )
    context.plone_utils.addPortalMessage('%s Item(s) cut.'%len(ids))
    return state
                                                
#return state.set(status='failure', portal_status_message='Please select one or more items to cut.')
context.plone_utils.addPortalMessage('Please select one or more items to cut.')
return state.set(status='failure')