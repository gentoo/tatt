"""Use Flag Mechanics """

import random
import re
import math
from portage.dep import check_required_use, dep_getcpv
from subprocess import *

from .tool import unique
from gentoolkit.flag import get_flags, reduce_flags

def all_valid_flags(flag):
    return True

## Useflag Combis ##
def findUseFlagCombis (package, config, port):
    """
    Generate combinations of use flags to test
    The output will be a list each containing a ready to use USE=... string
    """
    uselist = sorted(reduce_flags(get_flags(dep_getcpv(package.packageString()))))
    # The uselist could have duplicates due to slot-conditional
    # output of equery
    uselist=unique(uselist)
    for i in config['ignoreprefix']:
        uselist=[u for u in uselist if not re.match(i,u)]

    if config['usecombis'] == 0:
        # Do only all and nothing:
        swlist = [0,2**(len(uselist))-1]
    # Test if we can exhaust all USE-combis by computing the binary logarithm.
    elif len(uselist) > math.log(config['usecombis'],2):
        # Generate a sample of USE combis
        s = 2**(len (uselist))
        random.seed()
        swlist = [random.randint(0, s-1) for i in range (config['usecombis'])]
        swlist.append(0)
        swlist.append(s-1)
        swlist.sort()
        swlist = unique(swlist)
    else:
        # Yes we can: generate all combinations
        swlist = list(range(2**len(uselist)))

    usecombis=[]
    ruse = " ".join(port.aux_get(dep_getcpv(package.packageString()), ["REQUIRED_USE"]))
    for sw in swlist:
        mod = []
        act = [] # check_required_use doesn't like -flag entries
        for pos in range(len(uselist)):
            if ((2**pos) & sw):
                mod.append("")
                act.append(uselist[pos])
            else:
                mod.append("-")
        if bool(check_required_use(ruse, " ".join(act), all_valid_flags)):
            uc = " ".join(["".join(uf) for uf in list(zip(mod, uselist))])
            usecombis.append(uc)
        else:
            print("  " + package.packageString() + ": ignoring invalid USE flag combination", act)

    # Merge everything to a USE="" string
    return ["USE=\'" + uc + "\'" for uc in usecombis]
