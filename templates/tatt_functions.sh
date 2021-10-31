#!/bin/bash

function tatt_pkg_error
{
  local eout=${2}

  echo "${eout}"

  if [ -n "${USE}" ]; then
    echo -n "USE='${USE}'" >> "${TATT_REPORTFILE}"
  fi
  if [ -n "${FEATURES}" ]; then
    echo -n " FEATURES='${FEATURES}'" >> "${TATT_REPORTFILE}"
  fi

  if [[ "${eout}" =~ REQUIRED_USE ]] ; then
    echo " : REQUIRED_USE not satisfied (probably) for ${1:?}" >> "${TATT_REPORTFILE}"
  elif [[ "${eout}" =~ USE\ changes ]] ; then
    echo " : USE dependencies not satisfied (probably) for ${1:?}" >> "${TATT_REPORTFILE}"
  elif [[ "${eout}" =~ keyword\ changes ]]; then
    echo " : unkeyworded dependencies (probably) for ${1:?}" >> "${TATT_REPORTFILE}"
  elif [[ "${eout}" =~ Error:\ circular\ dependencies: ]]; then
    echo " : circular dependencies (probably) for ${1:?}" >> "${TATT_REPORTFILE}"
  elif [[ "${eout}" =~ Blocked\ Packages ]]; then
    echo " : blocked packages (probably) for ${1:?}" >> "${TATT_REPORTFILE}"
  else
    echo " failed for ${1:?}" >> "${TATT_REPORTFILE}"
  fi

  CP=${1#=}
  BUILDDIR=/var/tmp/portage/${CP}
  BUILDLOG=${BUILDDIR}/temp/build.log
  if [[ -n "${TATT_BUILDLOGDIR}" && -s "${BUILDLOG}" ]]; then
    mkdir -p "${TATT_BUILDLOGDIR}"
    LOGNAME=$(mktemp -p "${TATT_BUILDLOGDIR}" "${CP/\//_}_${TATT_TEST_TYPE}_XXXXX")
    mv "${BUILDLOG}" "${LOGNAME}"
    echo "    log has been saved as ${LOGNAME}" >> "${TATT_REPORTFILE}"
    TESTLOGS=($(find ${BUILDDIR}/work -iname '*test*log*'))
    if [ ${#TESTLOGS[@]} -gt 0 ]; then
      tar cf ${LOGNAME}.tar ${TESTLOGS[@]}
      echo "    testsuite logs have been saved as ${LOGNAME}.tar" >> "${TATT_REPORTFILE}"
    fi
  fi
}

function tatt_test_pkg
{
  if [ "${1:?}" == "--test" ]; then
    shift

	# Do a first pass to avoid circular dependencies
	# --onlydeps should mean we're avoiding (too much) duplicate work
	USE="${USE} minimal -doc" emerge --onlydeps -q1 --with-test-deps ${TATT_EMERGEOPTS} "${1:?}"

    if ! emerge --onlydeps -q1 --with-test-deps ${TATT_EMERGEOPTS} "${1:?}"; then
      echo "merging test dependencies of ${1} failed" >> "${TATT_REPORTFILE}"
      return 1
    fi
    TFEATURES="${FEATURES} test"
  else
    TFEATURES="${FEATURES}"
  fi

  # --usepkg-exclude needs the package name, so let's extract it
  # from the atom we have
  local name=$(portageq pquery "${1:?}" -n)

  eout=$( FEATURES="${TFEATURES}" emerge -1 --getbinpkg=n --usepkg-exclude="${name}" ${TATT_EMERGEOPTS} "${1:?}" 2>&1 1>/dev/tty )
  if [[ $? == 0 ]] ; then
    if [ -n "${TFEATURES}" ]; then
      echo -n "FEATURES='${TFEATURES}' " >> "${TATT_REPORTFILE}"
    fi
    echo "USE='${USE}' succeeded for ${1:?}" >> "${TATT_REPORTFILE}"
  else
    FEATURES="${TFEATURES}" tatt_pkg_error "${1:?}" "${eout}"
    return 1
  fi
}
