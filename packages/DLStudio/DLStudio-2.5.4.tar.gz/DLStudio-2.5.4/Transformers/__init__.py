#!/usr/bin/env python

import sys

if sys.version_info[0] == 3:
    from DLStudio.DLStudio import __version__
    from DLStudio.DLStudio import __author__
    from DLStudio.DLStudio import __date__
    from DLStudio.DLStudio import __url__
    from DLStudio.DLStudio import __copyright__
    from Transformers.Transformers import TransformerFG
    from Transformers.Transformers import TransformerPreLN
    from Transformers.Transformers import visTransformer
else:
    sys.exit("The transformer code in DLStudio has only been tested for Python 3")




