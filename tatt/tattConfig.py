"""Abstraction of a tatt configuration"""

import os
import sys

# from configobj
from configobj import ConfigObj
from validate  import Validator
# To access the specfile:
from pkg_resources import resource_filename

# resource_filename will give us platform-independent access to the specfile
specfile = resource_filename('tatt', 'dot-tatt-spec')

# this validator will also do type conversion according to the spec file!
class tattConfig (ConfigObj):
    """Nothing special here, just a checked ConfigObj"""
    def __init__(self):
        # Read the config from ~/.tatt and create ConfigObj
        ConfigObj.__init__(self, os.path.join(os.path.expanduser("~"), ".tatt"), configspec=specfile)

        # Validate against the specfile
        validator = Validator()
        result = self.validate(validator)

        if result != True:
            print ("Config file validation failed!")
            print ("The following items could not be parsed")
            for k in result.keys():
                if result[k] == False:
                    print (k)
            sys.exit(1)
