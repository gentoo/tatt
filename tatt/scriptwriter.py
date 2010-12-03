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
def rdepTestString(pack):
    # We are checking for stable rdeps:
    rdeps = stablerdeps (pack)
    if len(rdeps) == 0:
        print(("No stable rdeps for " + pack.packageString()))
        return "# No stable rdeps \n"
    st = " "
    for r in rdeps:
        call = ""
        call = "FEATURES=\"test\" "
        call = (call + "USE=\"" + " ".join([s for s in r[1] if not s[0] == "!"]) + " ")
        call = (call + " ".join(["-" + s[1:] for s in r[1] if s[0] == "!"]))
        call = (call + "\" emerge -1v " + r[0])
        st = st + ("if " + call + "; then \n")
        # @@REPORT@@ will be replaced with the name of the reportfile further down
        st = (st + "echo \""+call.replace("\"","\'") + "\" succeeded >> " + "@@REPORT@@" + ";\n")
        st = (st + "else echo \""+call.replace("\"","\'") + "\" failed >> " + "@@REPORT@@" + ";\nfi;\n")
    return st

def writerdepscript(job, packlist):
    outfilename = (job + "-rdeps.sh")
    reportname = (job + ".report")
    if os.path.isfile(outfilename):
        print(("WARNING: Will overwrite " + outfilename))
    outfile = open(outfilename,'w')
    outfile.write("#!/bin/sh" + '\n')
    for p in packlist:
        outfile.write("# Code for " + p.packageCatName() + "\n")
        outfile.write(rdepTestString(p).replace("@@REPORT@@", reportname))
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
    return 0
