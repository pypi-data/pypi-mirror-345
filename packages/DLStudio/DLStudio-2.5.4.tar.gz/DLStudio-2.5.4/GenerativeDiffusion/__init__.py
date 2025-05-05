#!/usr/bin/env python

import sys

if sys.version_info[0] == 3:
    from DLStudio.DLStudio import __version__
    from DLStudio.DLStudio import __author__
    from DLStudio.DLStudio import __date__
    from DLStudio.DLStudio import __url__
    from DLStudio.DLStudio import __copyright__
    from GenerativeDiffusion.GenerativeDiffusion import GenerativeDiffusion
    from GenerativeDiffusion.GenerativeDiffusion import GaussianDiffusion
    from GenerativeDiffusion.GenerativeDiffusion import AttentionBlock
    from GenerativeDiffusion.GenerativeDiffusion import UNetModel
    from GenerativeDiffusion.GenerativeDiffusion import mUNet
else:                                                                                                                            
    sys.exit("The transformer code in DLStudio has only been tested for Python 3")




