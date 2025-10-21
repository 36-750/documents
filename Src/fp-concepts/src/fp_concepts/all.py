#
# Helper module to load all the names into the namespace
#
# Do 'from FP.all import *' to load all the needed objects.
#
# ruff: noqa: F401, F403, F405

from __future__ import annotations

from . import Monoids
from . import optics

from .Alternative import *
from .Applicative import *
from .Bicofunctor import *
from .Bifunctor   import *
from .CoFunctor   import *
from .Foldable    import *
from .Functor     import *
from .Monad       import *
from .Profunctor  import *
from .Traversable import *

from .Const       import *
from .Either      import *
from .Identity    import *
from .List        import *
from .Maybe       import *
from .NTuple      import *
from .Pair        import *

from .Dict        import *
from .Monoids     import Monoid, munit, mcombine
from .Reader      import *
from .Set         import *
from .State       import *
from .Trees       import *
from .Writer      import *

from .functions   import *
from .ops         import *
from .utils       import *
from .wrappers    import *

from .Pair        import pair  # More powerful version over .functions.pair

from .optics.all  import *

#
# Conveniences
#

c = compose
