#!/usr/bin/python

from gentooPackage import gentooPackage as gP
from subprocess import *
import sys
import re
import random
import os

############### GET THE CONFIGURATION ####################
import ConfigParser

def readConfig(file="~/.tatt"):
    config = ConfigParser.SafeConfigParser()
    config.read(file)
    print config.sections()
    atomre = config.get("general", "aromregexp")
    ## A list of useflagsprefixes to be ignored
    ignoreprefix= config.get("general", "ignoreprefix")
    ## Success Message:
    successmessage = config.get("general", "successmessage")
    print aromre
##########################################################

readConfig()
print successmessage
