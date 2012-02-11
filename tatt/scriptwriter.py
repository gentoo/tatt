""" Filling script templates """

import random
import os

from .usecombis import findUseFlagCombis
from .tinderbox import stablerdeps
from .tool import unique

#### USE-COMBIS ########

def useCombiTestString(pack, config):
    """ Build with diffent useflag combis """
    try:
        usesnippetfile=open(config['template-dir'] + "use-snippet", 'r')
    except IOError:
        print("use-snippet not found in " + config['template-dir'])
        exit(1)
    s = "" # This will contain the resulting string
    usesnippet = usesnippetfile.read()
    usesnippet = usesnippet.replace("@@CPV@@", pack.packageString() )
    usecombis = findUseFlagCombis (pack, config)
    for uc in usecombis:
        localsnippet = usesnippet.replace("@@USE@@", uc)
        localsnippet = localsnippet.replace("@@FEATURES@@", "")
        s = s + localsnippet
    # In the end we test once with tests and users flags
    localsnippet = usesnippet.replace("@@USE@@", " ")
    localsnippet = localsnippet.replace("@@FEATURES@@", "FEATURES=\"${FEATURES} test\"")
    s = s + localsnippet
    return s

def writeusecombiscript(job, config):
    # job is a tatt job object
    # config is a tatt configuration
    try:
        useheaderfile=open(config['template-dir'] + "use-header", 'r')
    except IOError:
        print("use-header not found in " + config['template-dir'])
        exit(1)
    useheader=useheaderfile.read().replace("@@JOB@@", job.name)
    outfilename = (job.name + "-useflags.sh")
    reportname = (job.name + ".report")
    if os.path.isfile(outfilename):
        print(("WARNING: Will overwrite " + outfilename))
    outfile = open(outfilename, 'w')
    outfile.write(useheader)
    for p in job.packageList:
        outfile.write("# Code for " + p.packageCatName() + "\n")
        outfile.write(useCombiTestString(p, config).replace("@@REPORTFILE@@",reportname))
    outfile.close()

######################################

############ RDEPS ################
def rdepTestString(rdep, config):
    try:
        rdepsnippetfile=open(config['template-dir'] + "revdep-snippet", 'r')
    except IOError:
        print("revdep-snippet not found in " + config['template-dir'])
        exit(1)
    rdepsnippet=rdepsnippetfile.read()
    snip = rdepsnippet.replace("@@FEATURES@@", "FEATURES=\"${FEATURES} test\"")
    ustring = "USE=\'" + " ".join([st for st in rdep[1] if not st[0] == "!"]) + " "
    ustring = ustring + " ".join(["-" + st[1:] for st in rdep[1] if st[0] == "!"]) + "\'"
    snip = snip.replace("@@USE@@", ustring)
    snip = snip.replace("@@CPV@@", rdep[0] )
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
    try:
        rdepheaderfile=open(config['template-dir'] + "revdep-header", 'r')
    except IOError:
        print("revdep-header not found in " + config['template-dir'])
        exit(1)
    rdepheader=rdepheaderfile.read().replace("@@JOB@@", job.name)
    outfilename = (job.name + "-rdeps.sh")
    reportname = (job.name + ".report")
    if os.path.isfile(outfilename):
        print(("WARNING: Will overwrite " + outfilename))
    outfile = open(outfilename,'w')
    outfile.write(rdepheader)

    for r in rdeps:
        # Todo: remove duplicates
        localsnippet = rdepTestString (r, config)
        outfile.write(localsnippet.replace("@@REPORTFILE@@", reportname))
    outfile.close()


#######Write report script############
def writesucessreportscript (job, config):
    outfilename = (job.name + "-success.sh")
    reportname = (job.name + ".report")
    if os.path.isfile(outfilename):
        print(("WARNING: Will overwrite " + outfilename))
    outfile = open(outfilename,'w')
    outfile.write("#!/bin/sh" + '\n')
    outfile.write("if grep failed " + reportname + " >> /dev/null; then echo Failure found;\n")
    succmess = config['successmessage'].replace("@@ARCH@@", config['arch'])
    outfile.write("else bugz modify " + job.bugnumber + ' -c' + "\"" + succmess + "\";\n")
    outfile.write("fi;")
    outfile.close()
    print(("Success Report script written to " + outfilename))


####### Write the commit script #########
def writecommitscript (job, config):
    try:
        commitheaderfile=open(config['template-dir'] + "commit-header", 'r')
        commitsnippetfile=open(config['template-dir'] + "commit-snippet", 'r')
        commitsnippetfile2=open(config['template-dir'] + "commit-snippet-2", 'r')
        commitfooterfile=open(config['template-dir'] + "commit-footer", 'r')
    except IOError:
        print("Some commit template not found in " + config['template-dir'])
        exit(1)
    csnippet = commitsnippetfile.read().replace("@@JOB@@", job.name)
    csnippet2 = commitsnippetfile2.read().replace("@@JOB@@", job.name)
    outfilename = (job.name + "-commit.sh")
    if os.path.isfile(outfilename):
        print(("WARNING: Will overwrite " + outfilename))
    outfile = open(outfilename,'w')
    cheader = commitheaderfile.read().replace("@@JOB@@", job.name)
    cheader = cheader.replace("@@REPODIR@@", config['repodir'])
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
        s = csnippet.replace("@@BUG@@", job.bugnumber)
        s = s.replace("@@ARCH@@", config['arch'])
        if job.type=="stable":
            newkeyword=config['arch']
        elif job.type=="keyword":
            newkeyword="~"+config['arch']
        else:
            print "No job type? Can't continue. This is a bug"
            exit(1)
        s = s.replace("@@NEWKEYWORD@@", newkeyword)
        # Prepare a list of ebuild names strings
        ebuilds = [p.packageName()+"-"+p.packageVersion()+".ebuild" for p in packageHash[pack]]
        s = s.replace("@@EBUILD@@", " ".join(ebuilds))
        s = s.replace("@@CP@@", pack)
        outfile.write(s)
    # Second round: repoman -d full checks and commit, should be done once per
    # key of packageHash
    for pack in packageHash.keys():
        s = csnippet2.replace("@@BUG@@", job.bugnumber)
        s = s.replace("@@ARCH@@", config['arch'])
        s = s.replace("@@NEWKEYWORD@@", newkeyword)
        # Prepare a list of ebuild names strings
        ebuilds = [p.packageName()+"-"+p.packageVersion()+".ebuild" for p in packageHash[pack]]
        s = s.replace("@@EBUILD@@", " ".join(ebuilds))
        s = s.replace("@@CP@@", pack)
        outfile.write(s)
    # Footer (committing)
    outfile.write (commitfooterfile.read().replace("@@ARCH@@", config['arch']).replace("@@BUG@@", job.bugnumber))
    outfile.close()
    print(("Commit script written to " + outfilename))


######## Write clean-up script ##############
def writeCleanUpScript (job, config):
    try:
        cleanUpTemplate=open(config['template-dir'] + "cleanup", 'r')
    except IOError:
        print("Clean-Up template not found in" + config['template-dir'])
        print "No clean-up script written"
        return
    script = cleanUpTemplate.read().replace("@@JOB@@", job.name)
    script = script.replace("@@CPV@@", job.name)
    script = script.replace("@@KEYWORDFILE@@", config['unmaskfile'])
    outfilename = (job.name + "-cleanup.sh")
    if os.path.isfile(outfilename):
        print(("WARNING: Will overwrite " + outfilename))
    outfile = open(outfilename,'w')
    outfile.write(script)
