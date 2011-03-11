"""Use Flag Mechanics """

import random
import re
import math
from subprocess import *

from .tool import unique

## Useflag Combis ##
def findUseFlagCombis (package, config):
    """
    Generate combinations of use flags to test
    The output will be a list each containing a ready to use USE=... string
    """
    uses=Popen('equery -C uses '+package.packageString()+' | cut -f 1 | cut -c 2-40 | xargs',
               shell=True, stdout=PIPE).communicate()[0]
    uselist=uses.split()
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
    for sw in swlist:
        mod = []
        for pos in range(len(uselist)):
            if ((2**pos) & sw):
                mod.append("")
            else:
                mod.append("-")
        usecombis.append(list(zip(mod, uselist)))

    usecombis = [["".join(uf) for uf in combi] for combi in usecombis]

    # Merge everything to a USE="" string
    return ["USE=\'"+" ".join(uc)+ "\'" for uc in usecombis]
