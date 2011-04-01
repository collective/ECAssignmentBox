# -*- coding: utf-8 -*-
# $Id$
#
# Copyright (c) 2006-2011 Otto-von-Guericke-UniversitŠt Magdeburg
#
# This file is part of ECAssignmentBox.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'

# Workflow Scripts for: ecassignmentbox_workflow

def sendGradedEmail(self, state_change, **kw):
    """
    """
    state_change.object.sendGradingNotificationEmail()
