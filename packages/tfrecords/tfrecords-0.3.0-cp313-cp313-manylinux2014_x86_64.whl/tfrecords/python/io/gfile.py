# @Time    : 2022/9/21 19:48
# @Author  : tk
# @FileName: gfile.py

from .file_io import copy_v2 as copy
from .file_io import create_dir_v2 as mkdir
from .file_io import delete_file_v2 as remove
from .file_io import delete_recursively_v2 as rmtree
from .file_io import file_exists_v2 as exists
from .file_io import get_matching_files_v2 as glob
from .file_io import get_registered_schemes
from .file_io import is_directory_v2 as isdir
from .file_io import join
from .file_io import list_directory_v2 as listdir
from .file_io import recursive_create_dir_v2 as makedirs
from .file_io import rename_v2 as rename
from .file_io import stat_v2 as stat
from .file_io import walk_v2 as walk
