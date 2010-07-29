import sys
sys.path.append('../tatt')

from packageFinder import findPackages as fP
import re
atomre = re.compile("=?[^\s:,;<>]+/\S+-?[0-9]?\S+[0-9][^\s:,;<>]?[a-z]*")
s1 = "Stabilize games-strategy/freeciv-2.2.1"
s2 = """media-fonts/mikachan-font-otf-9.1-r1 ppc64
media-fonts/mikachan-font-ttf-8.9-r2 ppc64
x11-apps/beforelight-1.0.1 ppc ppc64 sparc
x11-apps/grandr-0.1 arm
x11-apps/ico-1.0.2 ppc ppc64 sparc
x11-apps/mkfontscale-1.0.6 ppc64
x11-apps/oclock-1.0.1 ia64
x11-apps/rstart-1.0.3 sparc
x11-apps/scripts-1.0.1 ppc ppc64 sparc
x11-apps/smproxy-1.0.3 ppc64
x11-apps/xdbedizzy-1.0.2 sparc
x11-apps/xdm-1.1.9 alpha ia64 ppc64 s390 sh sparc
x11-apps/xf86dga-1.0.2 ppc64
x11-apps/xkbcomp-1.1.0 ppc64
x11-apps/xkbprint-1.0.2 sparc
x11-apps/xmore-1.0.1-r1 sparc
x11-apps/xstdcmap-1.0.1 sparc
x11-apps/xtrap-1.0.2 sparc
x11-drivers/linuxwacom-0.8.4_p1 ppc ppc64
x11-drivers/xf86-input-joystick-1.5.0 hppa
x11-drivers/xf86-video-ati-6.12.1-r1 alpha
x11-drivers/xf86-video-radeonhd-1.2.5 ppc64
x11-drivers/xf86-video-xgi-1.5.1 ppc ppc64
x11-libs/libXCalibrate-0.1_pre20081207-r1 ppc64
x11-libs/libXxf86misc-1.0.2 ppc
x11-libs/libdrm-2.4.15 ppc64
x11-misc/driconf-0.9.1 sparc
x11-misc/rendercheck-1.3 sparc
x11-misc/transset-0.1_pre20040821 sparc
x11-misc/xtermcontrol-2.9 sparc
x11-proto/evieext-1.1.0 hppa ppc
x11-proto/xf86miscproto-0.9.3 ppc
x11-proto/xproto-7.0.15 ppc64
x11-themes/xcursor-themes-1.0.2 hppa
"""

for p in fP(s1, atomre):
    print p.packageString()

print "\n ----------- \n ------------ \n"    
for p in fP(s2, atomre):
    print p.packageString()

