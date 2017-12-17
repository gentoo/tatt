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

def check_uses(ruse, uselist, sw, package):
    act = [] # check_required_use doesn't like -flag entries
    for pos in range(len(uselist)):
        if ((2**pos) & sw):
            act.append(uselist[pos])
    if bool(check_required_use(ruse, " ".join(act), all_valid_flags)):
        return True
    else:
        print("  " + package.packageString() + ": ignoring invalid USE flag combination", act)
        return False

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

    ruse = " ".join(port.aux_get(dep_getcpv(package.packageString()), ["REQUIRED_USE"]))
    swlist = []
    if config['usecombis'] == 0:
        # Do only all and nothing:
        if check_uses(ruse, uselist, 0, package):
            swlist.append(0)
        if check_uses(ruse, uselist, 2**len(uselist) - 1):
            swlist.append(2**len(uselist) - 1)
    # Test if we can exhaust all USE-combis by computing the binary logarithm.
    elif len(uselist) > math.log(config['usecombis'],2):
        # Generate a sample of USE combis
        s = 2**(len (uselist))
        rnds = set()
        random.seed()
        while len(swlist) < config['usecombis'] and len(rnds) < config['usecombis']:
            r = random.randint(0, s-1)
            if r in rnds:
                # already checked
                continue

            if not check_uses(ruse, uselist, r, package):
                # invalid combination
                continue

            swlist.append(r)

        swlist.sort()
    else:
        # Yes we can: generate all combinations
        for pos in range(2**len(uselist)):
            if check_uses(ruse, uselist, pos, package):
                swlist.append(pos)

    usecombis=[]
    for sw in swlist:
        mod = []
        for pos in range(len(uselist)):
            if ((2**pos) & sw):
                mod.append("")
            else:
                mod.append("-")
        usecombis.append(" ".join(["".join(uf) for uf in list(zip(mod, uselist))]))

    # Merge everything to a USE="" string
    return ["USE=\'" + uc + "\'" for uc in usecombis]
