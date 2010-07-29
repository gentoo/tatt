import sys
sys.path.append('../tatt')

import tinderbox
from gentooPackage import gentooPackage as gp

p = gp("=media-sound/amarok-2.3.1-r2")
print tinderbox.stablerdeps (p)


