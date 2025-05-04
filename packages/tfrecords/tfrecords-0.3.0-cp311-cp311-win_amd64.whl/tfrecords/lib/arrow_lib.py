# -*- coding: utf-8 -*-
# @Time:  3:04
# @Author: tk
# @File：arrow_lib

import os
from tfrecords.lib.fix import fix_conda
try:
    from .arrow_cc import *
except Exception as e:
    if os.name == 'posix':
        fix_conda()
        from .arrow_cc import *
    else:
        raise e