#!/bin/bash

. /etc/init.d/functions.sh

if [ "$1" != "" ]; then
ebegin "running repoman and searching for bugs for package $1"
eend $?

cd /usr/portage/"$1"
repoman full
einfo "repoman completed"
eend $?

cd

bugz search -s all "$1"
einfo "bugz completed"
eend $?

else
    echo "Enter a package!"
fi

read -p "Enter the bug number: " bug_number
einfo "You entered $bug_number"
mkdir $bug_number
cd $bug_number
tatt -b$bug_number
for file in *
do
    if [ -f "$file" ];
    then
        chmod 777 $file
    fi
done
einfo "All good starting the test"
./*-rdeps.sh && ./*-useflags.sh


printf "\033[32m\nComment success on Bug? Enter: 0\033[m\n"
printf "\033[31m\nExit? Enter: 1\033[m\n"

read -p "Enter >> " comment
if [ $comment = "0" ]; then
./*-success.sh 
else
    exit 1
fi