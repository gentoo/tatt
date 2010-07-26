"""acessing the tinderbox at http://tinderbox.dev.gentoo.org/misc/dindex/ """

from gentooPackage import gentooPackage as gP
import urllib
import re
from subprocess import *

## Generate stable rdeps ###
def stablerdeps (package):
    """
    Find packages with stable versions which depend on atom
    We query the tinderbox at http://tinderbox.dev.gentoo.org/misc/dindex/
    for this purpose.
    The result is a list of pairs of package atoms and a list of necessary useflags
    """
    tinderbox = 'http://tinderbox.dev.gentoo.org/misc/dindex/'
    # File structure on this tinderbox equals that in the tree
    # Problem: The rdeps can be version dependent
    # nothing we can do about this here...
    atom = package.packageCatName()
    download = urllib.urlopen(tinderbox + atom).read()
    if not re.search("404 - Not Found", download) == None:
        return []
    # The result is a "\n" separated list of packages : useflags
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
        d[gP(s[0]).packageCatName()] = s[1]
    outlist2 = [[k, d[k]] for k in d.keys()]
    outlist = []
    for o in outlist2:
        # We are calling eix for each package to work around issues with --stable:
        # What we should do with a future version of eix is to do this in a single run!
        # Todo: Fork multiple eix instances 
        eixcall = ["eix", "--stable", "--only-names", "--exact", o[0]]
        p2 = Popen(eixcall, stdout=PIPE)
        out = p2.communicate()[0]
        if out == '': continue
        else : outlist.append(o)
    return outlist
    
#############################
