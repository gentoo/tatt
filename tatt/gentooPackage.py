"""Module for easy access to portage's atom syntax """

import re
from portage.dep import dep_getcpv, dep_getkey, isvalidatom

class gentooPackage(object):
    """A Gentoo package consists of:
       category
       name
       version
    of a Gentoo package"""

    def __init__(self, st):
        """An atom is initialized from an atom string"""
        if not isvalidatom(st):
            st = '=' + st
        cp = dep_getkey(st)
        self.ver = dep_getcpv(st)[len(cp) + 1:] # +1 to strip the leading '-'
        slashparts = cp.split("/")
        self.category = slashparts[0]
        self.name = slashparts[1]

    def packageName(self):
        """Returns the package name without category"""
        return self.name

    def packageVersion(self):
        """Returns the package version"""
        return self.ver

    def packageCategory(self):
        """Returns the package category without name"""
        return self.category

    def packageCatName(self):
        """Returns the package category and name without version"""
        return "/".join([self.category, self.name])

    def packageString(self):
        """ Returns a portage compatible string representation"""
        if self.ver == '':
            return  "/".join([self.category, self.name])
        else:
            return ( "=" + "/".join([self.category, "-".join([self.name, self.ver])]))
