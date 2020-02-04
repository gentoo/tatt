"""module for extracting packages from a package/architecture list """

from .gentooPackage import gentooPackage as gP

def findPackages (s, arch):
    """ Given a string s,
        and a string arch
        return all gentooPackages from that string that need actioning on that arch """

    packages = []

    for line in s.splitlines():
        if not line:
            continue
        atom, _, arches = line.replace('\t', ' ').partition(' ')
        archlist = arches.split(' ')
        if not arches or arch in archlist or ('~' + arch) in archlist:
            packages.append(gP(atom))

    return(packages)
