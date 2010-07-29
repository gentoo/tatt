""" Various methods to write test scripts """

import random
import os

from usecombis import findUseFlagCombis
from tinderbox import stablerdeps

#### USE-COMBIS ########

def useCombiTestString(pack, ignoreprefix):
    # Show or build with diffent useflag combis
    s = ""
    usecombis = findUseFlagCombis (pack, ignoreprefix)
    for uc in usecombis:
        s = s + "if " + uc + " emerge -1v " + pack.packageString() + "; then " + '\n'
        # @@REPORT@@ will be replaces by the name of the reportfile later
        s = s + "  echo \"" + uc.replace("\"","\'") + " succeeded \" >> " + "@@REPORT@@" + "; " + '\n'
        s = s + "else echo \"" + uc.replace("\"", "\'") + " failed \" >> " + "@@REPORT@@" + '; \nfi; \n'
        # In the end we test once with tests and users flags
        s = s + "FEATURES=\"test\" emerge -1v " + pack.packageString() + "\n"
    return s

def writeusecombiscript(job, packlist, ignoreprefix):
    outfilename = (job + "-useflags.sh")
    reportname = (job + ".report")
    if os.path.isfile(outfilename):
        print ("WARNING: Will overwrite " + outfilename)
    outfile = open(outfilename, 'w')
    outfile.write("#!/bin/sh" + '\n')
    for p in packlist:
        outfile.write("# Code for " + p.packageCatName() + "\n")
        outfile.write(useCombiTestString(p, ignoreprefix).replace("@@REPORT@@",reportname))
    outfile.close()

######################################

############ RDEPS ################
def rdepTestString(pack):
    # We are checking for stable rdeps:
    rdeps = stablerdeps (pack)
    if len(rdeps) == 0:
        print "No stable rdeps \n"
        return "# No stable rdeps \n"
    if len(rdeps) > 20:
        print "More than 20 stable rdeps, sampling 20 \n"
        rdeps = random.sample(rdeps, 20)
    st = " "
    print rdeps
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
        print ("WARNING: Will overwrite " + outfilename)
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
        print ("WARNING: Will overwrite " + outfilename)
    outfile = open(outfilename,'w')
    outfile.write("#!/bin/sh" + '\n')
    outfile.write("if grep failed " + reportname + " >> /dev/null; then echo Failure found;\n")
    outfile.write("else bugz modify " + bugnum + ' -c' + "\"" + success + "\";\n")
    outfile.write("fi;")
    outfile.close()
    print ("Success Report script written to " + outfilename)
    return 0
