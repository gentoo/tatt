"""Use Flag Mechanics """

import random
import re
import math
import itertools
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

def flag_combinations(flags):
    """ Yield all possible combinations of all possible sizes for ``flags``.

    Example: ['a', 'b', 'c'] -> [
        [],
        ['a'], ['b'], ['c'],
        ['a', 'b'], ['a', 'c'], ['b', 'c'],
        ['a', 'b', 'c'],
    ]
    """
    for i in range(len(flags)):
        # TODO: drop py2 and use "yield from"
        for comb in itertools.combinations(flags, i):
            yield comb


## Useflag Combis ##
def findUseFlagCombis(package, config, port):
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
    allcombs = list(flag_combinations(uselist))

    def check(comb):
        comb = list(set(comb) | alwayson)
        return bool(check_required_use(ruse, comb, lambda flag: True))

    combs = [c for c in allcombs if check(c)]
    print("{} valid combinations among {} possible ones".format(len(combs), len(allcombs)))
    if config['usecombis'] == 0:
        # Do only all and nothing, that is, the first and the last valid
        # combinations
        if len(combs) > 2:
            del combs[1:-1]
    # Test if we can exhaust all USE-combis by computing the binary logarithm.
    elif len(combs) > config['usecombis']:
        # Generate a sample of USE combis
        random.seed()
        combs = random.choices(combs, k=config['usecombis'])

    print("Chose {} combinations".format(len(combs)))

    result = []
    for comb in combs:
        line = []
        for flag in uselist:
            if flag in comb:
                line.append(flag)
            else:
                line.append('-' + flag)
        result.append(line)

    # Merge everything to a USE="" string
    return ["USE='{}'".format(' '.join(useflags)) for useflags in result]
