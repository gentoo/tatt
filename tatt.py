#!/usr/bin/python

import sys
import re
import random
from subprocess import *
import os

## Testing the validity of a package atom ##
def atomtest(atom):
    """ Test an string for being a portage atom"""
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
    What we will call is:
    equery depends ${ATOM} | eix --pipe --stable --only-names
    """
    eqarg = ["equery", "depends", "-a", atom]
    # For debugging purposes put your package list here:
    # eqarg = ["cat", "/home/tom/dump"]
    ## There is some bug in eix which makes the pipe thing nonworking.
    ## We will work around by looping manually:
    outlist = []
    p1 = Popen(eqarg, stdout=PIPE)
    out = p1.communicate()[0].rstrip()
    plist = out.split("\n")
    # A typical element of plist is games-util/xgamer-0.2.1-r17
    # We split at the last '-' before a number.
    # Does that make sense?
    for package in plist:
        # A problem for this are the -r* parts
        name = re.split("-[0-9]", package)[0]
        eixcall = ["eix", "--stable", "--only-names", "--exact", name]
        p2 = Popen(eixcall, stdout=PIPE)
        outlist.append(p2.communicate()[0].rstrip())
    outlist.sort()
    while outlist[0] == '':
        outlist.remove('')
        if len(outlist) == 0:
            return []
    return outlist
    
#############################

## Useflag Combis ##
def findUseFlagCombis (atom):
    """
    Generate combinations of use flags to test
    """
    uses=Popen('equery -C uses '+atom+' | cut -f 1 | cut -c 2-40 | xargs',
               shell=True, stdout=PIPE).communicate()[0]
    uselist=uses.split()

    if len(uselist) > 4:
        # More than 4 use flags, generate 16 random strings and everything -, everything +
        s = 2**(len (uselist))
        random.seed()
        swlist = [random.randint(0, s-1) for i in range (16)]
        swlist.append(0)
        swlist.append(s-1)
        swlist.sort()
        # Todo: Remove duplicates
    else:
        # 4 or less use flags. Generate all combinations
        swlist = range(2**len(uselist))

    usecombis=[]
    for sw in swlist:
        mod = []
        for pos in range(len(uselist)):
            if ((2**pos) & sw):
                mod.append("")
            else:
                mod.append("-")
        usecombis.append(zip(mod, uselist))

    usecombis = [["".join(uf) for uf in combi] for combi in usecombis]

    # Merge everything to as USE="" string
    return ["USE=\""+" ".join(uc)+ "\"" for uc in usecombis]

#####################################################

######### Main program starts here ###############

### USAGE and OPTIONS ###
from optparse import OptionParser

parser=OptionParser()
parser.add_option("-d", "--depend",
                  help="Determine stable rdeps",
                  dest="depend",
                  action="store_true",
                  default = False)
parser.add_option("-u", "--use" "--usecombis",
                  help="Determine use flag combinations",
                  dest="usecombi",
                  action="store_true",
                  default = False)
parser.add_option("-f", "--file", "-o",
                  help="Outfile name",
                  dest="fileprefix",
                  action="store",
                  default="tatt-test.sh"
                  )
parser.add_option("-p", "--pretend", 
                  help="Print things to stdout instead of doing them",
                  action="store_true",
                  default=False
                  )

(options,args) = parser.parse_args()

if (Popen(['whoami'], stdout=PIPE).communicate()[0].rstrip() == 'root'):
    isroot=True
else:
    print "You're not root!"
    isroot=False

try:
    atom = args[0]
except IndexError:
    print "Please call with package atom as argument"
    exit (1)

if options.depend:
    # We are checking for stable rdeps:
    rdeps = stableredeps (atom)
    if len(rdeps) == 0:
        print "No stable rdeps"
    else:
        outfilename = (atom.split("/")[1] + "-rdeptest.sh")
        if os.path.isfile(outfilename):
            print ("WARNING: Will overwrite " + outfilename)
        outfile = open(outfilename,'w')
        outfile.write(" && ".join(["emerge -1v " + r for r in rdeps]))
        outfile.close()
        print ("Rdep build commands written to " + outfilename)

if options.usecombi:
    # Show or build with diffent useflag combis
    usecombis = findUseFlagCombis (atom)
    outfilename = (atom.split("/")[1] + "-useflagtest.sh")
    if os.path.isfile(outfilename):
        print ("WARNING: Will overwrite " + outfilename)
    outfile = open(outfilename, 'w')        
    outfile.write(" && ".join([uc + " emerge -1v " + atom for uc in usecombis]))
    outfile.close()
    print ("Build commands written to " + outfilename)

## That's all folks ##
