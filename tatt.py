#!/usr/bin/python

from gentooPackage import gentooPackage as gP
from subprocess import *
import sys
import re
import random
import os

## Testing the validity of a package atom ##
def atomtest(atom):
    """ Test an string for being a portage atom"""
    ### Can we use stuff from portage here?
    testatom = re.compile('=?\\w+.*/.*')
    if testatom.match(atom) == None :
        print "Sorry, no valid package atom given"
        print "Use the version string starting with = and ending in the version"
        exit(1)
############################################

## Getting unique elements of a list ##
def unique(seq, idfun=None):
    # order preserving
    if idfun is None:
        def idfun(x): return x
        seen = {}
        result = []
        for item in seq:
            marker = idfun(item)
            # in old Python versions:
            # if seen.has_key(marker)
            # but in new ones:
            if marker in seen: continue
            seen[marker] = 1
            result.append(item)
    return result

## Generate stable rdeps ###
def stableredeps (atom):
    """
    Find packages with stable versions which depend on atom
    We query the tinderbox at http://tinderbox.dev.gentoo.org/misc/dindex/
    for this purpose.
    The result is a list of pairs of package atoms and a list of necessary useflags
    """

    #Todo, this will not work with atoms that specify verisons
    import urllib
    tinderbox = 'http://tinderbox.dev.gentoo.org/misc/dindex/'
    download = urllib.urlopen(tinderbox + atom).read()
    if not re.search("404 - Not Found", download) == None:
        return []
    packlist = download.rstrip().split("\n")
    # Split at : to see if useflags are necessary
    splitlist2 = [p.split(":") for p in packlist]
    # Fill with empty useflags if nothing is given:
    splitlist = []
    for s in splitlist2:
        if len(s) == 1:
            splitlist.append([s[0],[" "]])
        else:
            splitlist.append([s[0],s[1].split("+")])
    d = dict([])
    for s in splitlist:
        # Saves necessary useflags under package names, removing duplicates.
        d[gP(s[0]).packageName()] = s[1]
    return [[k, d[k]] for k in d.keys()]
    
#############################

## Useflag Combis ##
def findUseFlagCombis (atom):
    """
    Generate combinations of use flags to test
    """
    ## A list of useflagsprefixes to be ignored
    ignoreprefix=["elibc_","video_cards_","test","debug"]
    
    uses=Popen('equery -C uses '+atom+' | cut -f 1 | cut -c 2-40 | xargs',
               shell=True, stdout=PIPE).communicate()[0]
    uselist=uses.split()
    for i in ignoreprefix:
        uselist=[u for u in uselist if not re.match(i,u)]

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


#### Write useflagcombiscript ########
def writeusecombiscript(atom):
    # Show or build with diffent useflag combis
    usecombis = findUseFlagCombis (atom)
    outfilename = (atom.split("/")[1] + "-useflagtest.sh")
    if os.path.isfile(outfilename):
        print ("WARNING: Will overwrite " + outfilename)
    outfile = open(outfilename, 'w')
    if options.feature_test:
        outfile.write ("FEATURES=\"test\" ")
    outfile.write(" && ".join([uc + " emerge -1v " + atom for uc in usecombis]))
    outfile.close()
    print ("Build commands written to " + outfilename)
    return 0
######################################


### Write rdepcombiscript ############
def writerdepscript(atom):
    # We are checking for stable rdeps:
    rdeps = stableredeps (atom)
    if len(rdeps) == 0:
        print "No stable rdeps"
    else:
    	outfilename = (atom.split("/")[1] + "-rdeptest.sh")
    	if os.path.isfile(outfilename):
    	    print ("WARNING: Will overwrite " + outfilename)
    	outfile = open(outfilename,'w')
    	estrings = []
        print rdeps
    	for r in rdeps:
    	    st = ""
    	    if options.feature_test:
    	        st = (st + "FEATURES=\"test\" ")
    	    st = (st + "USE=\"" + " ".join([s for s in r[1] if not s[0] == "!"]) + " ")
    	    st = (st + " ".join(["-" + s[1:] for s in r[1] if s[0] == "!"]))
    	    st = (st + "\" emerge -1v =" + r[0])
    	    estrings.append(st)
    	outfile.write(" && ".join(estrings))
    	outfile.close()
    	print ("Rdep build commands written to " + outfilename)
    	return 0
######################################


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
parser.add_option("-t", "--test",
                  help="run emerge commands with FEATURES=\"test\"",
                  dest="feature_test",
                  action="store_true",
                  default = True)
parser.add_option("-b", "--bug",
                  help="do the full program for a given stable request bug",
                  dest="bugnum",
                  action="store")

(options,args) = parser.parse_args()

if (Popen(['whoami'], stdout=PIPE).communicate()[0].rstrip() == 'root'):
    isroot=True
else:
    print "You're not root!"
    isroot=False

## -b and a bugnumber was given ?
if options.bugnum:
    print "Working on bug number " + options.bugnum
    bugraw = Popen(['bugz', 'get', options.bugnum, '-n', '--skip-auth'], stdout=PIPE).communicate()[0]
    if not re.search('[Ss]tab', bugraw):
        print "Does not look like a stable request bug !"
        print bugraw
        exit (1)
    bugdata = bugraw.split("\n")
    
    atomre = re.compile("=?\S+-\S+/\S+-[0-9]\S+")
    for l in bugdata:
        m = atomre.search(l)
        if m == None: continue
        atom = m.group(0)
        break
    # Remove a leading =
    p = gP(atom)
    print "Found the following package atom : " + p.packageString()
    # Splitting the atom to get the package name:
    if isroot:
        # If we are root, then we can write to package.keywords
        keywordfile=open("/etc/portage/package.keywords/arch",'a')
        keywordfile.write("\n" + p.packageString() + "\n")
        keywordfile.close()
        print "Appended package to /etc/portage/package.keywords/arch"
    else:
        print "You are not root, your unmaskstring would be:"
        print ("\n" + p.packageString() + "\n")
    ## Write the scripts
    writeusecombiscript(p.packageName())
    writerdepscript(p.packageName())
    exit (0)

## If we arrive here then a package atom should be given
try:
    atom = args[0]
except IndexError:
    print "Please call with package atom as argument"
    exit (1)

if options.depend:
    writerdepscript(atom)

if options.usecombi:
    writeusecombiscript(atom)

## That's all folks ##
