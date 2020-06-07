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

def get_repo_dir(repodir):
    # Prefer the repo dir in the config
    if repodir:
        if os.path.isdir(repodir):
            return repodir
        else:
            raise ValueError("Repo dir does not seem to be a directory")

    # No path given in config
    if os.path.isdir("/var/db/repos/gentoo/"):
        print("Using /var/db/repos/gentoo/ as fallback")
        return "/var/db/repos/gentoo"
    elif os.path.isdir("/usr/portage/"):
        print("Using /usr/portage/ as fallback")
        return "/usr/portage/"

    raise ValueError("Repo dir not given and fallbacks failed")
