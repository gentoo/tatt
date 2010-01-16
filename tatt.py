#!/usr/bin/python

import sys
import re
import random
from subprocess import *
import os

## Testing the validity of a package atom ##
def atomtest(atom):
    ### A VERY SIMPLE regular expression to test for a package atom ####
    ### Can we use stuff from portage here?
    testa = re.compile('=?\\w+.*/.*')
    if testa.match(atom) == None :
        print "Sorry, no valid package atom given"
        print "Use the version string starting with = and ending in the version"
        exit(1)
############################################

## Generate stable rdeps ###
def stableredeps (atom):
    """
    Find packages with stable versions which depend on atom
    """
    pass
#############################

## Useflag Combis ##
def findUseFlagCombis (atom):
    """
    Generate combinations of use flags to test
    """
    pass
#####################

######### Main program starts here ###############


### USAGE and OPTIONS ###
from optparse import OptionParser

parser=OptionParser()
parser.add_option("-d", "--depend", help="Determine stable rdeps")
parser.add_option("-f", "--file", "-o", help="Outfile name")
    
(options,args) = parser.parse_args()

if os.path.isfile(options.file):
    print ("WARNING! "+options.file+" exsits. I will overwrite it!")

outfile = open(options.file,'w')

if (Popen(['whoami'], stdout=PIPE).communicate()[0].rstrip() == 'root'):
    isroot=True
else:
    print "You're not root!"
    isroot=False
    
try:
    atom = args[1]
except IndexError:
    print "Please call with package atom as argument"
    exit (1)

print (options,args)

## That's all folks ##
