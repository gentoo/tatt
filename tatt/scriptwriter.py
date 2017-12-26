""" Filling script templates """

import random
import os
import portage
import sys

from .usecombis import findUseFlagCombis
from .tinderbox import stablerdeps
from .tool import unique

#### USE-COMBIS ########

def scriptTemplate(jobname, config, filename):
    """ open snippet file and replace common placeholders """
    try:
        snippetfile=open(config['template-dir'] + filename, 'r')
    except IOError:
        print("use-snippet not found in " + config['template-dir'])
        sys.exit(1)

    reportname = jobname + ".report"

    snippet = snippetfile.read()
    snippet = snippet.replace("@@EMERGEOPTS@@", config['emergeopts'])
    snippet = snippet.replace("@@JOB@@", jobname)
    snippet = snippet.replace("@@ARCH@@", config['arch'])
    snippet = snippet.replace("@@REPORTFILE@@", reportname)
    snippet = snippet.replace("@@BUILDLOGDIR@@", config['buildlogdir'])
    return snippet

def useCombiTestString(jobname, pack, config, port):
    """ Build with diffent useflag combis """
    usesnippet = scriptTemplate(jobname, config, "use-snippet")

    s = "" # This will contain the resulting string
    usesnippet = usesnippet.replace("@@CPV@@", pack.packageString() )
    usecombis = findUseFlagCombis (pack, config, port)
    for uc in usecombis:
        localsnippet = usesnippet.replace("@@USE@@", uc)
        localsnippet = localsnippet.replace("@@FEATURES@@", "")
        s = s + localsnippet
    # In the end we test once with tests and users flags
    localsnippet = usesnippet.replace("@@USE@@", "")
    localsnippet = localsnippet.replace("@@FEATURES@@", "FEATURES=\"${FEATURES} test\"")
    s = s + localsnippet
    return s

def writeusecombiscript(job, config):
    # job is a tatt job object
    # config is a tatt configuration
    useheader = scriptTemplate(job.name, config, "use-header")

    outfilename = (job.name + "-useflags.sh")
    reportname = (job.name + ".report")
    if os.path.isfile(outfilename):
        print("WARNING: Will overwrite " + outfilename)
    outfile = open(outfilename, 'w')
    outfile.write(useheader)
    port = portage.db[portage.root]["porttree"].dbapi
    for p in job.packageList:
        outfile.write("\n# Code for " + p.packageString() + "\n")
        outfile.write(useCombiTestString(job.name, p, config, port))
        outfile.write("echo >> " + reportname + "\n")
    # Note: fchmod needs the filedescriptor which is an internal
    # integer retrieved by fileno().
    os.fchmod(outfile.fileno(), 0o744)  # rwxr--r--
    outfile.close()

######################################

############ RDEPS ################
def rdepTestString(jobname, rdep, config):
    rdepsnippet = scriptTemplate(jobname, config, "revdep-snippet")

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
    rdepheader = scriptTemplate(job.name, config, "revdep-header")
    outfilename = (job.name + "-rdeps.sh")
    if os.path.isfile(outfilename):
        print("WARNING: Will overwrite " + outfilename)
    outfile = open(outfilename,'w')
    outfile.write(rdepheader)

    for r in rdeps:
        # Todo: remove duplicates
        outfile.write(rdepTestString(job.name, r, config))
    os.fchmod(outfile.fileno(), 0o744)
    outfile.close()


#######Write report script############
def writesucessreportscript (job, config):
    outfilename = (job.name + "-success.sh")
    reportname = (job.name + ".report")
    if os.path.isfile(outfilename):
        print("WARNING: Will overwrite " + outfilename)
    try:
        updatebugtemplate=open(config['template-dir'] + "updatebug", 'r')
    except IOError:
        print("updatebug not found in " + config['template-dir'])
        sys.exit(1)
    updatebug=updatebugtemplate.read().replace("@@ARCH@@", config['arch'])
    updatebug=updatebug.replace("@@BUG@@", job.bugnumber)
    outfile = open(outfilename,'w')
    outfile.write(updatebug)
    os.fchmod(outfile.fileno(), 0o744)
    outfile.close()
    print("Success Report script written to " + outfilename)


####### Write the commit script #########
def writecommitscript (job, config):
    try:
        commitheaderfile=open(config['template-dir'] + "commit-header", 'r')
        commitsnippetfile=open(config['template-dir'] + "commit-snippet", 'r')
        commitsnippetfile2=open(config['template-dir'] + "commit-snippet-2", 'r')
        commitfooterfile=open(config['template-dir'] + "commit-footer", 'r')
    except IOError:
        print("Some commit template not found in " + config['template-dir'])
        sys.exit(1)
    csnippet = commitsnippetfile.read().replace("@@JOB@@", job.name)
    csnippet2 = commitsnippetfile2.read().replace("@@JOB@@", job.name)
    outfilename = (job.name + "-commit.sh")
    if os.path.isfile(outfilename):
        print("WARNING: Will overwrite " + outfilename)
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
            print ("No job type? Can't continue. This is a bug")
            sys.exit(1)
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
    os.fchmod(outfile.fileno(), 0o744)
    outfile.close()
    print("Commit script written to " + outfilename)


######## Write clean-up script ##############
def writeCleanUpScript (job, config):
    try:
        cleanUpTemplate=open(config['template-dir'] + "cleanup", 'r')
    except IOError:
        print("Clean-Up template not found in" + config['template-dir'])
        print("No clean-up script written")
        return
    script = cleanUpTemplate.read().replace("@@JOB@@", job.name)
    script = script.replace("@@CPV@@", job.name)
    script = script.replace("@@KEYWORDFILE@@", config['unmaskfile'])
    outfilename = (job.name + "-cleanup.sh")
    if os.path.isfile(outfilename):
        print("WARNING: Will overwrite " + outfilename)
    outfile = open(outfilename,'w')
    outfile.write(script)
    os.fchmod(outfile.fileno(), 0o744)
    outfile.close()
