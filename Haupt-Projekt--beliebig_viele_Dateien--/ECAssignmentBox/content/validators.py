# -*- coding: utf-8 -*-
# $Id: validators.py 1599 2011-10-07 12:16:45Z amelung $
#
# Copyright (c) 2006-2011 Otto-von-Guericke-UniversitŠt Magdeburg
#
# This file is part of ECAssignmentBox.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'

from zope.interface import implements

from Products.validation import validation
from Products.validation.interfaces.IValidator import IValidator

POSITIVE_NUMBER_VALIDATOR_NAME = 'isPositive'

class PositiveNumberValidator:
    """
    """
    
    #__implements__ = IValidator
    implements(IValidator)

    def __init__(self, name, title='', description=''):
        """
        """
        self.name = name
        self.title = title or name
        self.description = description
    
    def __call__(self, value, *args, **kwargs):
        """
        """
        try:
            nval = float(value)
        except ValueError:
            return ("Validation failed (%(name)s): could not convert \
            '%(value)r' to number" % { 'name' : self.name, 'value': value})

        if nval >= 0:
            return True

        return ("Validation failed: '%(value)s' is not a positive number." %
                { 'value': value, })

# register validator 
isPositive = PositiveNumberValidator(POSITIVE_NUMBER_VALIDATOR_NAME)
validation.register(isPositive)
