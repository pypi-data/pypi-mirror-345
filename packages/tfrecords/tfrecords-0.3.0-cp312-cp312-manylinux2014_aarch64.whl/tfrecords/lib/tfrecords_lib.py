# -*- coding: utf-8 -*-
# @Time:  3:05
# @Author: tk
# @File：tfrecords_lib
import os
from tfrecords.lib.fix import fix_conda
try:
    from .tfrecords_cc import *
except Exception as e:
    if os.name == 'posix':
        lib_file = os.path.join(os.path.dirname(__file__), "tfrecords_cc.so")
        fix_conda()
        from .tfrecords_cc import *
    else:
        raise e