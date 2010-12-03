#!/bin/bash

# Drop initial -m if given
[[ "${1}" == "-m" ]] && shift

[[ -z "${1}" ]] && {
	echo " *** missing change description"
	exit 1
}

[[ -z "$(cvs up 2>&1 | grep '^[MAR]')" ]] && {
	echo " *** no changes!"
	exit 1
}

message="${1}"
echo "Using commit message:"
echo "${message}"

rm -f ChangeLog
cvs up ChangeLog 2>&1 | grep -v "cvs update: warning: \`ChangeLog' was lost"

echangelog "${message}" || {
	echo " *** echangelog failed"
	exit 1
}

ebuild $(\ls -1 *.ebuild | tail -n 1) manifest
repoman full || {
	echo " *** repoman failed"
	exit 1
}
repoman -m "${message}" commit
