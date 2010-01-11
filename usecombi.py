#!/usr/bin/python

import sys
import re
import random
from subprocess import *
import os

if os.path.isfile("usecombi.out"):
    print "WARNING! usecombi.out exsits. I will overwrite it!"

outfile = open("usecombi.out",'w')

if (Popen(['whoami'], stdout=PIPE).communicate()[0].rstrip() == 'root'):
    isroot=True
else:
    print "You're not root!"
    isroot=False

try:
    atom = sys.argv[1]
except IndexError:
    print "Please call package atom as argument"
    exit (1)

# A VERY SIMPLE regular expression to test for a package atom
atomtest = re.compile('=?\\w+.*/.*')
if atomtest.match(atom) == None :
    print "Sorry, no valid package atom given"
    print "Use the version string starting with = and ending in the version"
    exit(1)

# get the useflags
uses=Popen('equery -C uses '+atom+' | cut -f 1 | cut -c 2-40 | xargs',shell=True,stdout=PIPE).communicate()[0]

uselist=uses.split()

# Here is my naive subset iterator
# usecombis = [[ x for (pos,x) in zip(range(len(uselist)),uselist)
#              if (2**pos) & switches] for switches in range(2**len(uselist))]

usecombis=[]
for sw in range(2**len(uselist)):
    mod = []
    for pos in range(len(uselist)):
        if ((2**pos) & sw):
            mod.append("")
        else:
            mod.append("-")
    usecombis.append(zip(mod,uselist))

usecombis = [["".join(uf) for uf in combi] for combi in usecombis]

# If more than 5 useflags, pick 32 combis at random.
if len(usecombis)>32:
    random.seed()
    usecombis = random.sample(usecombis, 32)

for uc in usecombis:
    ucs = " ".join(uc) # The string with USE+"..."
    callstring = 'USE="'+ucs+'" emerge -1v '+'"'+atom+'"'
    if isroot:
        mes = ("Will now run : \n " + callstring)
        outfile.write(mes)
        print mes
        retvalue = call(callstring,shell=True)
        if retvalue > 0:
            mes = "returnvalue > 0 !"
            print mes
            outfile.write(mes+"\n")
        else:
            outfile.write("\n ==> OK \n")
        outfile.flush()
    else:
        print callstring
