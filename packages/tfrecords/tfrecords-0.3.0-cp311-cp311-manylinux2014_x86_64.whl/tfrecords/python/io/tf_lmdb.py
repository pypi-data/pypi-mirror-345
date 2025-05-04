# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""For reading and writing TFTables files."""
import os
import typing
from tfrecords.python.util import compat
from ...lib.tfrecords_lib import lmdb as _pywrap_db_io


__all__ = [
  'LmdbOptions',
  'LmdbIterater',
  'Lmdb',
  'LmdbFlag',
]

class LmdbFlag:
  MDB_FIXEDMAP =	0x01
  MDB_NOSUBDIR=	0x4000
  MDB_NOSYNC	=	0x10000
  MDB_RDONLY=		0x20000
  MDB_NOMETASYNC	=	0x40000
  MDB_WRITEMAP=		0x80000
  MDB_MAPASYNC=		0x100000
  MDB_NOTLS	=	0x200000
  MDB_NOLOCK	=	0x400000
  MDB_NORDAHEAD=	0x800000
  MDB_NOMEMINIT=	0x1000000
  MDB_PREVSNAPSHOT=	0x2000000
  MDB_REVERSEKEY=	0x02
  MDB_DUPSORT	=	0x04
  MDB_INTEGERKEY=	0x08
  MDB_DUPFIXED=	0x10
  MDB_INTEGERDUP=	0x20
  MDB_REVERSEDUP=	0x40
  MDB_CREATE	=	0x40000
  MDB_NOOVERWRITE=	0x10
  MDB_NODUPDATA=	0x20
  MDB_CURRENT	=0x40
  MDB_RESERVE	= 0x10000
  MDB_APPEND=	0x20000
  MDB_APPENDDUP=	0x40000
  MDB_MULTIPLE=	0x80000
  MDB_CP_COMPACT=	0x01


class LmdbOptions(object):

  def __init__(self,
                env_open_flag = 0,
                env_open_mode = 0o664, # 8进制表示
                txn_flag = 0,
                dbi_flag = 0,
                put_flag = 0
               ):

    """
    Args:
      env_open_flag: int or `None`.
      env_open_mode: int or `None`.
      txn_flag: int or `None`.
      dbi_flag: int or `None`.
      put_flag: int or `None`.

    Returns:
      A `TFTableOptions` object.

    Raises:
      ValueError: If compression_type is invalid.
    """
    # pylint: enable=line-too-long
    # Check compression_type is valid, but for backwards compatibility don't
    # immediately convert to a string.
    self.options = _pywrap_db_io.LmdbOptions()

    if env_open_flag is not None:
      self.options.env_open_flag = env_open_flag

    if env_open_mode is not None:
      self.options.env_open_mode = env_open_mode

    if txn_flag is not None:
      self.options.txn_flag = txn_flag

    if dbi_flag is not None:
      self.options.dbi_flag = dbi_flag

    if put_flag is not None:
      self.options.put_flag = put_flag




  def __reduce_ex__(self, *args, **kwargs):
      return self.__class__,(self.options.env_open_flag,
                             self.options.env_open_mode,
                             self.options.txn_flag,
                             self.options.dbi_flag,
                             self.options.put_flag)

  def as_options(self):
    return self.options


class LmdbIterater(_pywrap_db_io.LmdbIterater):
  def __init__(self,*args,**kwargs):
    super(LmdbIterater, self).__init__(*args, **kwargs)

  def __del__(self):
    self.close()
    super(LmdbIterater, self).__del__()


  def __iter__(self):
    raise NotImplementedError

  def __next__(self):
    raise NotImplementedError

  def Valid(self):
    return super(LmdbIterater, self).Valid()
  
  def current(self):
    return super(LmdbIterater, self).current()

  def next(self):
    return super(LmdbIterater, self).next()

  def prev(self):
    return super(LmdbIterater, self).prev()

  def SeekToFirst(self):
    return super(LmdbIterater, self).SeekToFirst()

  def SeekToLast(self):
    return super(LmdbIterater, self).SeekToLast()
  
  def Seek(self,key):
    return super(LmdbIterater, self).Seek(key)

  def close(self):
    super(LmdbIterater, self).close()




class Lmdb(_pywrap_db_io.Lmdb):
  iterator_list = []
  def __init__(self, path : str,
               options: typing.Union[str , LmdbOptions],
               map_size : int,
               max_readers: int = 128,
               max_dbs: int=0
               ):
    """Opens file `path` and creates a `TFTableWriter` writing to it.

    Args:
      path: The path to the TFTables file.
      options: (optional) LmdbOptions .
      map_size: int  nmap file size

    Raises:
      IOError: If `path` cannot be opened for writing.
    """
    if not isinstance(options, LmdbOptions):
      options = LmdbOptions()

    if not os.path.exists(path) or (os.path.exists(path) and os.path.isfile(path)):
      os.mkdir(path)

    super(Lmdb, self).__init__(path, options.as_options(),map_size,max_readers,max_dbs)
    assert self.status() ==0 , self.error()
    self.path = path
    self.options = options
    self.map_size = map_size

  def __reduce_ex__(self, *args, **kwargs):
    return self.__class__, (self.path,
                            self.options,
                            self.map_size)

  def __del__(self):
    self.close()

  def get_iterater(self, reverse=False) -> LmdbIterater:
    it = super(Lmdb, self).get_iterater(reverse)
    self.iterator_list.append(it)
    return it

  def get(self, key: typing.Union[str , bytes], value=None):
    try:
      return super(Lmdb, self).get(key)
    except:
      pass
    return value

  def put_batch(self, keys : typing.List[typing.Union[str , bytes]],values : typing.List[typing.Union[str , bytes]]):
    return super(Lmdb, self).put_batch(keys,values)

  def put(self, key : typing.Union[str , bytes],value : typing.Union[str , bytes]):
    return super(Lmdb, self).put(key, value)

  def remove(self, key: typing.Union[str, bytes]):
    return super(Lmdb, self).remove(key)

  def close(self):
    """Close the file."""
    for it in self.iterator_list:
      if it is not None:
        it.close()
    self.iterator_list.clear()
    super(Lmdb, self).close()

  def error(self) -> str:
    return super(Lmdb, self).error()

  def status(self) -> int:
    return super(Lmdb, self).status()

