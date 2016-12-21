"""module for extracting packages from a package/architecture list """

from .gentooPackage import gentooPackage as gP

def findPackages (s, arch):
    """ Given a string s,
        and a string arch
        return all gentooPackages from that string that need actioning on that arch """

    packages = []

    for line in s.splitlines():
        atom, _, arches = line.partition(' ')
        if not arches or arch in arches.split(' '):
            packages.append(gP(atom))

    return(packages)
