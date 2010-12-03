"""acessing the tinderbox at http://tinderbox.dev.gentoo.org/misc/dindex/ """

import socket # For setting a global timeout
import urllib.request, urllib.error, urllib.parse
from subprocess import *
import random

from .gentooPackage import gentooPackage as gP

## TODO: Make the number of rdeps to sample a config option
## Pass the config on to this function:

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

    socket.setdefaulttimeout(45)
    try:
        download = urllib.request.urlopen(tinderbox + atom).read()
    except urllib.error.HTTPError as e:
        # Cleanup the timeout:
        socket.setdefaulttimeout(None)
        if e.code == 404:
            # 404 is OK, the package has no stable rdeps
            return []
        else:
            # Some other error should not occur:
            print("Non 404 Error on accessing the tinderbox")
            exit (1)
    # If we are here everything is fine, cleanup the timeout:
    socket.setdefaulttimeout(None)
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
    outlist2 = [[k, d[k]] for k in list(d.keys())]
    outlist = []
    # outlist 2 is setup at this point, to cut it down we sample randomly
    # without replacement until the list is empty or we have 20.
    
    # We are calling eix for each package to work around issues with --stable:
    # What we should do with a future version of eix is to do this in a single run!
    # Todo: Fork multiple eix instances 

    while ((len (outlist2) > 0) and (len(outlist) < 20)):
        # Warning: sample returns a list, even if only one sample
        [samp]=random.sample(outlist2, 1)
        # Drop the one we selected
        outlist2.remove(samp)
        eixcall = ["eix", "--stable", "--only-names", "--exact", samp[0]]
        p2 = Popen(eixcall, stdout=PIPE)
        out = p2.communicate()[0]
        if out == '': continue
        else : outlist.append(samp)
        
    if len(outlist) > 19:
        print("More than 20 stable rdeps, sampled 20. \n")
    return outlist
    
#############################
