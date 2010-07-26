"""module for identifying package names in files and strings"""

import re
from gentooPackage import gentooPackage as gP

def findPackages (s, regexp):
    """ Given a string s,
        and a compiled regexp regexp
        return all gentooPacakges that can be identified in the string"""
    
    # Should it be this simple?
    return [gP(ps) for ps in  re.findall(regexp, s)]
    # Yes, it is...

