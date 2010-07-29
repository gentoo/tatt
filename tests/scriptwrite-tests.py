import sys
sys.path.append('../tatt')

from scriptwriter import *
from gentooPackage import gentooPackage as gP

print useCombiTestString(gP("=media-sound/amarok-2.3.1-r2"),[])
