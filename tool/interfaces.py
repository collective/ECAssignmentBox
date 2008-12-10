# -*- coding: utf-8 -*-
# $Id: ECAssignmentBox.py,v 1.1.2.9 2008/10/24 09:06:57 amelung Exp $
#
# Copyright (c) 2006-2008 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECAssignmentBox.
#
# ECAssignmentBox is free software; you can redistribute it and/or 
# modify it under the terms of the GNU General Public License as 
# published by the Free Software Foundation; either version 2 of the 
# License, or (at your option) any later version.
#
# ECAssignmentBox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ECAssignmentBox; if not, write to the 
# Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, 
# MA  02110-1301  USA
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'
__version__   = '$Revision: 1.1 $'

from zope.interface import Interface

##code-section HEAD
##/code-section HEAD

class IECABTool(Interface):
    """Marker interface for .ECABTool.ECABTool
    """

##code-section FOOT
##/code-section FOOT