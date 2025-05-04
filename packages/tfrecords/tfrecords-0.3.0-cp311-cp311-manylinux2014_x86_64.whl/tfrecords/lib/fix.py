# -*- coding: utf-8 -*-
# @Time:  3:03
# @Author: tk
# @File：fix
import os
def execute_cmd(command):
    if os.name == 'posix':
        result = os.popen(command).read()
    else:
        command = f'cmd /c "{command}"'
        result = os.popen(command).read()
    return result



def fix_conda():
    lib_file = os.path.join(os.path.dirname(__file__), "arrow_cc.so")
    execute_cmd("patchelf --set-rpath {}/lib {}".format(os.environ.get('CONDA_PREFIX', ""), lib_file))

    lib_file = os.path.join(os.path.dirname(__file__), "tfrecords_cc.so")
    execute_cmd("patchelf --set-rpath {}/lib {}".format(os.environ.get('CONDA_PREFIX', ""), lib_file))


