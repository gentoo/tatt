# Copyright 1999-2010 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

EAPI="2"
SUPPORT_PYTHON_ABIS="1"

inherit distutils git

DESCRIPTION="tatt is an arch testing tool"
HOMEPAGE="http://github.com/tom111/tatt"
EGIT_REPO_URI="git://github.com/tom111/tatt.git"

LICENSE="GPL-2"
SLOT="0"
KEYWORDS=""
IUSE="+templates"

DEPEND="dev-python/setuptools"
RDEPEND="app-portage/eix
		app-portage/gentoolkit
		www-client/pybugz
		dev-python/configobj"

#configobj does not support python-3
RESTRICT_PYTHON_ABIS="3.*"

S="${WORKDIR}/${PN}"

src_install() {
	distutils_src_install
	if use templates; then
		insinto "/usr/share/${PN}"
		doins -r templates || die
	fi
	dodoc tatt.1
}

