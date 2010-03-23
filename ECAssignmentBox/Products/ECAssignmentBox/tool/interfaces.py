# -*- coding: utf-8 -*-
# $Id: interfaces.py 1291 2009-09-27 18:23:31Z amelung $
#
# Copyright (c) 2006-2009 Otto-von-Guericke University Magdeburg
#
# This file is part of ECAssignmentBox.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'
__version__   = '$Revision: 1.2 $'

from zope.interface import Interface

class IECABTool(Interface):
    """Marker interface for .ECABTool.ECABTool
    """
