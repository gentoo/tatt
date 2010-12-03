""" Filling script templates """

import random
import os

from .usecombis import findUseFlagCombis
from .tinderbox import stablerdeps

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
    localsnippet = localsnippet.replace("@@FEATURES@@", "FEATURES='test'")
    s = s + localsnippet
    return s

def writeusecombiscript(job, packlist, config):
    try:
        useheaderfile=open(config['template-dir'] + "use-header", 'r')
    except IOError:
        print("use-header not found in " + config['template-dir'])
        exit(1)
    useheader=useheaderfile.read().replace("@@JOB@@", job)
    outfilename = (job + "-useflags.sh")
    reportname = (job + ".report")
    if os.path.isfile(outfilename):
        print(("WARNING: Will overwrite " + outfilename))
    outfile = open(outfilename, 'w')
    outfile.write(useheader)
    for p in packlist:
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
    snip = rdepsnippet.replace("@@FEATURES@@", "FEATURES='test'")
    ustring = "USE=\'" + " ".join([st for st in rdep[1] if not st[0] == "!"]) + " "
    ustring = ustring + " ".join(["-" + st[1:] for st in rdep[1] if st[0] == "!"]) + "\'"
    snip = snip.replace("@@USE@@", ustring)
    snip = snip.replace("@@CPV@@", rdep[0] )
    return snip

def writerdepscript(job, packlist, config):
    # Populate the list of rdeps
    rdeps = []
    for p in packlist:
        rdeps = rdeps + stablerdeps (p)
    if len(rdeps) == 0:
        print("No stable rdeps for " + job)
        return

    # If there are rdeps, write the script
    try:
        rdepheaderfile=open(config['template-dir'] + "revdep-header", 'r')
    except IOError:
        print("revdep-header not found in " + config['template-dir'])
        exit(1)
    rdepheader=rdepheaderfile.read().replace("@@JOB@@", job)
    outfilename = (job + "-rdeps.sh")
    reportname = (job + ".report")
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
def writesucessreportscript (job, bugnum, success):
    outfilename = (job + "-success.sh")
    reportname = (job + ".report")
    if os.path.isfile(outfilename):
        print(("WARNING: Will overwrite " + outfilename))
    outfile = open(outfilename,'w')
    outfile.write("#!/bin/sh" + '\n')
    outfile.write("if grep failed " + reportname + " >> /dev/null; then echo Failure found;\n")
    outfile.write("else bugz modify " + bugnum + ' -c' + "\"" + success + "\";\n")
    outfile.write("fi;")
    outfile.close()
    print(("Success Report script written to " + outfilename))


####### Write the commit script #########
def writecommitscript (job, bugnum, packlist, config):
    try:
        commitheaderfile=open(config['template-dir'] + "commit-header", 'r')
        commitsnippetfile=open(config['template-dir'] + "commit-snippet", 'r')
    except IOError:
        print("commit-header or commit-snippet not found in " + config['template-dir'])
        exit(1)
    csnippet = commitsnippetfile.read().replace("@@JOB@@", job)    
    outfilename = (job + "-commit.sh")
    if os.path.isfile(outfilename):
        print(("WARNING: Will overwrite " + outfilename))
    outfile = open(outfilename,'w')
    outfile.write (commitheaderfile.read().replace("@@JOB@@", job))
    for pack in packlist:
        s = csnippet.replace("@@BUG@@", bugnum)
        s = s.replace("@@ARCH@@", config['arch'])
        s = s.replace("@@EBUILD@@", pack.packageCatName()+"-"+pack.packageVersion()+".ebuild")
        s = s.replace("@@CP@@", pack.packageCatName())
        outfile.write(s)
    outfile.close()
    print(("Commit script written to " + outfilename))

