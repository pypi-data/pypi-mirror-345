# -*- coding: utf-8 -*-
# @Time    : 2022/9/8 15:49

from tfrecords import LMDB
db_path = 'd:/tmp/example_lmdb'
def test_write(db_path):
    options = LMDB.LmdbOptions(env_open_flag = 0,
                env_open_mode = 0o664, # 8进制表示
                txn_flag = 0,
                dbi_flag = 0,
                put_flag = 0)
    file_writer = LMDB.Lmdb(db_path,options,map_size=1024 * 1024 * 10)
    keys, values = [], []
    for i in range(30):
        keys.append(b"input_" + str(i).encode())
        keys.append(b"label_" + str(i).encode())
        values.append(b"xiaoming_" + str(i).encode())
        values.append(b"zzs_" + str(i).encode())
        if (i + 1) % 1000 == 0:
            file_writer.put_batch(keys, values)
            keys.clear()
            values.clear()
    if len(keys):
        file_writer.put_batch(keys, values)
    file_writer.close()
def test_read(db_path):
    options = LMDB.LmdbOptions( env_open_flag = LMDB.LmdbFlag.MDB_RDONLY,
                env_open_mode = 0o664, # 8进制表示
                txn_flag = 0, # LMDB.LmdbFlag.MDB_RDONLY
                dbi_flag = 0,
                put_flag = 0)
    reader = LMDB.Lmdb(db_path,options,map_size= 0)

    def show():
        it = reader.get_iterater(reverse=False)
        i = 0
        for item in it:
            print(i,item)
            i += 1
    show()

    # def test_find(key):
    #     value = reader.get(key)
    #     print('find', type(value), value)
    # test_find('input0')
    # test_find('input5')
    # test_find(b'input10')

    reader.close()


test_write(db_path)
test_read(db_path)