"""Use Flag Mechanics """

import random
import re
import math
import portage
from portage.dep import check_required_use, dep_getcpv
from subprocess import *

from .tool import unique
from gentoolkit.flag import get_flags, reduce_flags

def enabled_use_flags(package):
    """ Returns enabled USE flags for ``package`` on the current system.
    """
    cpv = dep_getcpv(package.packageString())
    # TODO: don't hardcode porttree ROOT
    porttree = portage.db['/']['porttree'].dbapi
    settings = porttree.settings
    settings.unlock()
    settings.setcpv(cpv, mydb=portage.portdb)
    res = set(settings['PORTAGE_USE'].split())
    settings.reset()
    settings.lock()
    return res

def all_valid_flags(flag):
    return True

def check_uses(ruse, uselist, alwayson, sw, package):
    act = alwayson # check_required_use doesn't like -flag entries
    for pos in range(len(uselist)):
        if ((2**pos) & sw):
            act.add(uselist[pos])
    if bool(check_required_use(ruse, list(act), all_valid_flags)):
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
    # when we ignore USE flags, we have to check which one of them are enabled
    # on the system. These flags greatly influence the outcome of
    # check_required_use() and we have to consider them.
    alwayson = set()
    enabled_flags = enabled_use_flags(package)
    for prefix in config['ignoreprefix']:
        toremove = {u for u in uselist if re.match(prefix, u)}
        for u in toremove:
            if u in enabled_flags:
                alwayson.add(u)
            uselist.remove(u)

    ruse = " ".join(port.aux_get(dep_getcpv(package.packageString()), ["REQUIRED_USE"]))
    swlist = []
    if config['usecombis'] == 0:
        # Do only all and nothing:
        if check_uses(ruse, uselist, alwayson.copy(), 0, package):
            swlist.append(0)
        if check_uses(ruse, uselist, alwayson.copy(), 2**len(uselist) - 1, package):
            swlist.append(2**len(uselist) - 1)
    # Test if we can exhaust all USE-combis by computing the binary logarithm.
    elif len(uselist) > math.log(config['usecombis'],2):
        # Generate a sample of USE combis
        s = 2**(len (uselist))
        rnds = set()
        random.seed()
        while len(swlist) < config['usecombis'] and len(rnds) < s:
            r = random.randint(0, s-1)
            if r in rnds:
                # already checked
                continue
            rnds.add(r)

            if not check_uses(ruse, uselist, alwayson.copy(), r, package):
                # invalid combination
                continue

            swlist.append(r)

        swlist.sort()
    else:
        # Yes we can: generate all combinations
        for pos in range(2**len(uselist)):
            if check_uses(ruse, uselist, alwayson.copy(), pos, package):
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
