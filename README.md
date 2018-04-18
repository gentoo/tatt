tatt (is an) arch testing tool

Introduction
============

Arch testing includes many boring tasks and tatt tries to automate
them.  It can be configured through the file ~/.tatt, an example is
given below.

tatt uses a template system.  Basically it fills in small bash scripts
using data scraped off bugzilla.  You can look at the default
templates which live in /usr/share/tatt/templates/

tatt uses 'bugz' from www-client/pybugz.  You may want to configure an
alias for 'bugz' to contain your login-credentials or you will have to
type them everytime you use tatt.

tatt lives on GitHub.  Forks and pull requests are welcome:
https://github.com/gentoo/tatt

Ways to use tatt
================

Work on a stable bug no 300000
------------------------------

This will unmask the package and create five shell scripts.  One is
for automated testing of USE-flag combinations, one is for testing of
reverse dependencies, one is for committing the new keywords to CVS, one
is for leaving a message on the bug, and finally one is for cleaning up.

    tatt -b300000 -j myjob

 -j specifies a jobname which will be a prefix for the scripts that
tatt produces, if it is left empty the bugnumber will be used

Work on multiple packages
-------------------------

If a whole list of packages should be tested, they can be specified
in a file

    tatt -f myPackageFile -b bugnumber

This will open the file myPackageFile, look for all atoms in it, and
write scripts that test/commit all packages.  If -j is omitted the
filename is used.  The bugnumber is necessary for the commit script.

Resolving a bug
---------------

Assume everything was committed and we want to resolve the bug.

    tatt -r bugnum -m "x86 stable, Thanks xyz"

removes your arch from the CC field of the bug and adds the message.

    tatt -cr bugnum -m "x86 stable, Thanks, closing"

Does the things -r does and additionally closes the bug.

Running individual parts of tatt
--------------------------------

- Open a bug and leave a message (for instance after successfull
 testing)

    tatt -s300000

- Create only the test script for reverse dependencies of foo:

    tatt -d app-bar/foo

- Create only the USE-flag testing script of foo

    tatt -u app-bar/foo

- Show help 

    tatt -h 

* Configuring tatt via ~/.tatt
The specification of the configuration file can be found in dot-tatt-spec which usually resides
/usr/lib/${python}/site-packages/tatt

```shell
####### EXAMPLE ~/.tatt ############
# Here we show the possible options together with their default values

# Message for the success script @@ARCH@@ will be replaced by arch
# successmessage='Archtested on @@ARCH@@: Everything fine'

# ignoreprefix contains a list of use flag prefixes to be ignored 
# ignoreprefix="elibc_","video_cards_","linguas_","python_targets_","python_single_target_","kdeenablefinal","test","debug"

# The arch you are working on (be careful, only tested with x86)
# arch=x86

# Directory where your script templates are (normally you don't need
# to change this)
# template-dir="/usr/share/tatt/templates/"

# Where do you want tatt to put unmasked packages.
# unmaskfile="/etc/portage/package.keywords/archtest"

# You can customize the maximal number of rdeps to be tested as follows:
# rdeps=3

# You can customize the maximal number USE combis to be tested as follows:
# usecombis=3
# Note that All USE-flags on and all USE-flags off will always be tested.

# Location of a checked out CVS Gentoo tree for repoman checks and commit scripts
# repodir="./gentoo-x86"

# Url where the pre-generated rindex is to be found
# tinderbox-url="http://qa-reports.gentoo.org/output/genrdeps/rindex/"

# If this is set, then tatt will refuse to run in a directory that does not
# match this string.  Use it as a safety measure against creating tatt-scripts
# in random places of you filesystem
# safedir=string(default="")

# All emerge runs in the generated scripts are automatically passed
# the -1 option.  Here you can specify additional options.
# emergeopts="-v"

# directory where logs of failed builds will be stored
# the exact name of the log will be shown in the report file
# buildlogdir="./tatt/logs"
```
