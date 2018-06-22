""" Filling script templates """

import random
import os
import portage
import sys

from .usecombis import findUseFlagCombis
from .tinderbox import stablerdeps
from .tool import unique

#### USE-COMBIS ########

def scriptTemplate(job, config, filename):
    """ open snippet file and replace common placeholders """
    try:
        snippetfile=open(config['template-dir'] + filename, 'r')
    except IOError:
        print("template " + filename + " not found in " + config['template-dir'])
        sys.exit(1)

    reportname = job.name + ".report"
    if job.type == "stable":
        newkeyword = config['arch']
    elif job.type == "keyword":
        newkeyword = "~" + config['arch']
    else:
        print ("No job type? Can't continue. This is a bug")
        sys.exit(1)

    snippet = snippetfile.read()
    snippet = snippet.replace("@@EMERGEOPTS@@", config['emergeopts'])
    if job.bugnumber:
        snippet = snippet.replace("@@BUG@@", job.bugnumber)
    else:
        snippet = snippet.replace("@@BUG@@", '')
    snippet = snippet.replace("@@JOB@@", job.name)
    snippet = snippet.replace("@@ARCH@@", config['arch'])
    snippet = snippet.replace("@@REPODIR@@", config['repodir'])
    snippet = snippet.replace("@@REPORTFILE@@", reportname)
    snippet = snippet.replace("@@BUILDLOGDIR@@", config['buildlogdir'])
    snippet = snippet.replace("@@KEYWORDFILE@@", config['unmaskfile'])
    snippet = snippet.replace("@@NEWKEYWORD@@", newkeyword)
    snippet = snippet.replace("@@TEMPLATEDIR@@", config['template-dir'])
    return snippet

def useCombiTestString(job, pack, config, port):
    """ Build with diffent useflag combis """
    usesnippet = scriptTemplate(job, config, "use-snippet")
    usesnippet = usesnippet.replace("@@CPV@@", pack.packageString() )

    # test once with tests and users flags
    # do this first to trigger bugs in some packages where the test suite relies on
    # the package being already installed
    localsnippet = usesnippet.replace("@@USE@@", "")
    localsnippet = localsnippet.replace("@@FEATURES@@", "FEATURES=\"${FEATURES} test\"")
    s = localsnippet

    usecombis = findUseFlagCombis (pack, config, port)
    for uc in usecombis:
        localsnippet = usesnippet.replace("@@USE@@", uc)
        localsnippet = localsnippet.replace("@@FEATURES@@", "")
        s = s + localsnippet
    return s

def writeusecombiscript(job, config):
    # job is a tatt job object
    # config is a tatt configuration
    useheader = scriptTemplate(job, config, "use-header")

    outfilename = (job.name + "-useflags.sh")
    reportname = (job.name + ".report")
    if os.path.isfile(outfilename):
        print("WARNING: Will overwrite " + outfilename)
    outfile = open(outfilename, 'w')
    outfile.write(useheader)
    port = portage.db[portage.root]["porttree"].dbapi
    for p in job.packageList:
        outfile.write("\n# Code for " + p.packageString() + "\n")
        outfile.write(useCombiTestString(job, p, config, port))
        outfile.write("echo >> " + reportname + "\n")
    # Note: fchmod needs the filedescriptor which is an internal
    # integer retrieved by fileno().
    os.fchmod(outfile.fileno(), 0o744)  # rwxr--r--
    outfile.close()

######################################

############ RDEPS ################
def rdepTestString(job, rdep, config):
    rdepsnippet = scriptTemplate(job, config, "revdep-snippet")

    snip = rdepsnippet.replace("@@FEATURES@@", "FEATURES=\"${FEATURES} test\"")
    uflags = []
    for st in rdep[1]:
        st = st.strip()
        if len(st) == 0:
            continue
        if st[0] == "!":
            uflags.append("-" + st[1:])
        else:
            uflags.append(st)
    ustring = "USE=\'" + " ".join(uflags) + "\'"
    snip = snip.replace("@@USE@@", ustring)
    snip = snip.replace("@@CPV@@", rdep[0] )
    snip = snip.replace("@@EMERGEOPTS@@", config['emergeopts'])
    return snip

def writerdepscript(job, config):
    # Populate the list of rdeps
    rdeps = []
    for p in job.packageList:
        rdeps = rdeps + stablerdeps (p, config)
    if len(rdeps) == 0:
        print("No stable rdeps for " + job.name)
        return

    # If there are rdeps, write the script
    rdepheader = scriptTemplate(job, config, "revdep-header")
    outfilename = (job.name + "-rdeps.sh")
    if os.path.isfile(outfilename):
        print("WARNING: Will overwrite " + outfilename)
    outfile = open(outfilename,'w')
    outfile.write(rdepheader)

    for r in rdeps:
        # Todo: remove duplicates
        outfile.write(rdepTestString(job, r, config))
    os.fchmod(outfile.fileno(), 0o744)
    outfile.close()


#######Write report script############
def writesucessreportscript (job, config):
    outfilename = (job.name + "-success.sh")
    if os.path.isfile(outfilename):
        print("WARNING: Will overwrite " + outfilename)
    updatebug = scriptTemplate(job, config, "updatebug")
    outfile = open(outfilename,'w')
    outfile.write(updatebug)
    os.fchmod(outfile.fileno(), 0o744)
    outfile.close()
    print("Success Report script written to " + outfilename)


####### Write the commit script #########
def writecommitscript (job, config):
    cheader = scriptTemplate(job, config, "commit-header")
    csnippet = scriptTemplate(job, config, "commit-snippet")
    csnippet2 = scriptTemplate(job, config, "commit-snippet-2")
    cfooter = scriptTemplate(job, config, "commit-footer")

    outfilename = (job.name + "-commit.sh")
    if os.path.isfile(outfilename):
        print("WARNING: Will overwrite " + outfilename)
    outfile = open(outfilename,'w')
    outfile.write (cheader)
    # Here's a catch: If there are multiple versions of the same package to be
    # stabilized, then we want only one keywording block and one commit block
    # for them.  Therefore we split up the loop by sorting job.packlist
    # accordingly, saving them in a hash-table with the package names as keys
    # and the packages as values.
    packageHash = dict();
    for pack in job.packageList:
        if pack.packageCatName() in packageHash:
            packageHash[pack.packageCatName()] = packageHash[pack.packageCatName()] + [pack]
        else:
            packageHash[pack.packageCatName()] = [pack]
    # First round (ekeyword)
    for pack in packageHash.keys():
        # Prepare a list of ebuild names strings
        ebuilds = [p.packageName()+"-"+p.packageVersion()+".ebuild" for p in packageHash[pack]]
        s = csnippet.replace("@@EBUILD@@", " ".join(ebuilds))
        s = s.replace("@@CP@@", pack)
        outfile.write(s)
    # Second round: repoman -d full checks and commit, should be done once per
    # key of packageHash
    for pack in packageHash.keys():
        # Prepare a list of ebuild names strings
        ebuilds = [p.packageName()+"-"+p.packageVersion()+".ebuild" for p in packageHash[pack]]
        s = csnippet2.replace("@@EBUILD@@", " ".join(ebuilds))
        s = s.replace("@@CP@@", pack)
        outfile.write(s)
    # Footer (committing)
    outfile.write(cfooter)
    os.fchmod(outfile.fileno(), 0o744)
    outfile.close()
    print("Commit script written to " + outfilename)


######## Write clean-up script ##############
def writeCleanUpScript (job, config):
    script = scriptTemplate(job, config, "cleanup")
    outfilename = (job.name + "-cleanup.sh")
    if os.path.isfile(outfilename):
        print("WARNING: Will overwrite " + outfilename)
    outfile = open(outfilename,'w')
    outfile.write(script)
    os.fchmod(outfile.fileno(), 0o744)
    outfile.close()
