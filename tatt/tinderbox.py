"""acessing the tinderbox at http://tinderbox.dev.gentoo.org/misc/dindex/ """

import socket # For setting a global timeout
# Support python2 and python3 versions of urllib:
try:
    from urllib2 import urlopen, HTTPError
except:
    from urllib.request import urlopen
    from urllib.error import HTTPError
import sys
from subprocess import *
import random

from .gentooPackage import gentooPackage as gP

## TODO: Make the number of rdeps to sample a config option
## Pass the config on to this function:

## Generate stable rdeps ###
def stablerdeps (package, config):
    """
    Find packages with stable versions which depend on atom
    We query the tinderbox at http://tinderbox.dev.gentoo.org/misc/dindex/
    for this purpose.
    The result is a list of pairs of package atoms and a list of necessary useflags
    """
    tinderbox = config['tinderbox-url']
    # File structure on this tinderbox equals that in the tree
    # Problem: The rdeps can be version dependent
    # nothing we can do about this here...
    atom = package.packageCatName()

    socket.setdefaulttimeout(45)
    try:
        download = urlopen(tinderbox + atom).read()
    except HTTPError as e:
        # Cleanup the timeout:
        socket.setdefaulttimeout(None)
        if e.code == 404:
            # 404 is OK, the package has no stable rdeps
            return []
        else:
            # Some other error should not occur:
            print("Non 404 Error on accessing the tinderbox")
            sys.exit (1)
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
    # outlist2 is set up at this point.  It contains all candidates.  To cut it down we sample
    # randomly without replacement until the list is empty or we have config['rdeps'] many.

    # We are calling eix for each package to work around issues with --stable:
    # What we should do with a future version of eix is to do this in a single run
    # or fork multiple eix instances

    while ((len (outlist2) > 0) and (len(outlist) < config['rdeps'])):
        # Warning: sample returns a list, even if only one sample
        [samp]=random.sample(outlist2, 1)
        # Drop the one we selected
        outlist2.remove(samp)
        eixcall = ["eix", "--stable", "--only-names", "--exact", samp[0]]
        p2 = Popen(eixcall, stdout=PIPE)
        out = p2.communicate()[0].decode('utf-8')
        if out == '': continue
        else : outlist.append(samp)

    if len(outlist) > config['rdeps']:
        print("More than " + config['rdeps'] + " stable rdeps, took a sample. \n")
    return outlist
#############################
