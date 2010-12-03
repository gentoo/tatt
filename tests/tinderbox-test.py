import sys
sys.path.append('../tatt')

import tinderbox
from gentooPackage import gentooPackage as gp

# Has a stable rdep:
p = gp("=media-sound/amarok-2.3.1-r2")
print(tinderbox.stablerdeps (p))

# A pacakge without stable rdeps:
p = gp("=app-portage/tatt-9999")
print(tinderbox.stablerdeps (p))
