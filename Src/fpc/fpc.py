#
# Helper module to load all the names into the namespace
#
# Do 'from fpc import *' to load all the needed objects.
#

from __future__ import annotations

import Monoid as Monoids
import Trees

from Functor     import *
from Applicative import *
from Monad       import *
from Bifunctor   import *
from Traversable import *

from Const       import Const, runConst, makeConst
from Identity    import Identity

from List        import List
from Either      import *
from Maybe       import *
from Pair        import *

from Trees       import *
from Monoid      import Monoid, munit, mcombine

from functions   import *
from lens        import *
from utils       import Collect


#
# Conveniences
#

c = compose
