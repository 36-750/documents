#
# Helper module to load all the names into the namespace
#
# Do 'from FP.all import *' to load all the needed objects.
#

from __future__ import annotations

from . import Monoids
from . import Trees

from .Functor     import *
from .Applicative import *
from .Monad       import *
from .CoFunctor   import *
from .Bifunctor   import *
from .Foldable    import *
from .Traversable import *
from .Profunctor  import *

from .List        import *
from .Maybe       import *
from .Either      import *
from .Pair        import *
from .Const       import *
from .Identity    import *
from .NTuple      import *

from .Monoids     import Monoid, munit, mcombine
from .Set         import *
from .Dict        import *
from .State       import *
from .Trees       import *

from .functions   import *
from .optics      import *
from .ops         import *
from .utils       import *


#
# Conveniences
#

c = compose
