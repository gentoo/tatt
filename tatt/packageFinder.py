"""module for extracting packages from a package/architecture list """
import subprocess
from .gentooPackage import gentooPackage as gP

def findPackages (s, arch, repo, bugnum=False):
    """ Given a string s, a string arch, a string path to the repo, and
        an integer bugnum, return all gentooPackages from that string
        that need actioning on that arch """

    packages = []

    if bugnum:
            print("Using Nattka to process the bug")
            output = subprocess.check_output(['nattka', '--repo', repo, 'apply', '-a', arch.replace("~", ""), '-n', bugnum, '--ignore-sanity-check', '--ignore-dependencies'])
            output = output.decode("utf8").split("\n")
            output = [line for line in output if not line.startswith("#")]
            output = [line.split(" ")[0] for line in output]
    else:
            print("Manually processing")
            output = s.splitlines()

    for line in output:
        if not line:
            continue

        atom, _, arches = line.replace('\t', ' ').partition(' ')
        archlist = arches.split(' ')
        if not arches or arch in archlist or ('~' + arch) in archlist:
            packages.append(gP(atom))

    return(packages)
