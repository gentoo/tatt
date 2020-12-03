import os

""" Helper functions used in tatt"""

## Getting unique elements of a list ##
def unique(seq, idfun=None):
    """Returns the unique elements in a list
    order preserving"""
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
