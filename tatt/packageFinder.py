"""module for extracting packages from a package/architecture list """
from .gentooPackage import gentooPackage as gP

def findPackages (s, arch, repo, bugnum=False):
    """ Given a string s, a string arch, a string path to the repo, and
        an integer bugnum, return all gentooPackages from that string
        that need actioning on that arch """

    if bugnum:
        from nattka.bugzilla import NattkaBugzilla
        from nattka.package import find_repository, match_package_list, PackageListEmpty
        from pathlib import Path

        _, repo = find_repository(Path(repo))
        nattka_bugzilla = NattkaBugzilla(api_key=None)
        arch = arch.replace("~", "")
        try:
            bug = next(iter(nattka_bugzilla.find_bugs(
                bugs=[int(bugnum)],
                unresolved=True,
                sanity_check=[True],
                cc=f'{arch}@gentoo.org',
            ).values()))
            pkgs = dict(match_package_list(repo, bug, only_new=True, filter_arch=[arch], permit_allarches=True)).keys()
            return [gP(f'{pkg.category}/{pkg.PF}') for pkg in pkgs]
        except PackageListEmpty:
            return []
    else:
        print("Manually processing")
        packages = []
        for line in s.splitlines():
            if not line:
                continue

            atom, _, arches = line.replace('\t', ' ').partition(' ')
            archlist = arches.split(' ')
            if not arches or arch in archlist or ('~' + arch) in archlist:
                packages.append(gP(atom))

        return(packages)
