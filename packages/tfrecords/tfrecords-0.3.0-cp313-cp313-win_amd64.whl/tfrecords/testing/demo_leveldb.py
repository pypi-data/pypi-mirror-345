# -*- coding: utf-8 -*-
# @Time    : 2022/9/8 15:49

from tfrecords import LEVELDB
db_path = 'd:/tmp/example_leveldb'
def test_write(db_path):
    options = LEVELDB.LeveldbOptions(create_if_missing=True, error_if_exists=False)
    file_writer = LEVELDB.Leveldb(db_path,options)

    keys,values = [],[]
    for i in range(30):
        keys.append(b"input_" + str(i).encode())
        keys.append(b"label_" + str(i).encode())
        values.append(b"xiaoming" + str(i).encode())
        values.append(b"zzs" + str(i).encode())
        if (i + 1) % 1000 == 0:
            file_writer.put_batch(keys,values)
            keys.clear()
            values.clear()
    if len(keys):
        file_writer.put_batch(keys, values)
        keys.clear()
        values.clear()

    file_writer.close()
def test_read(db_path):
    options = LEVELDB.LeveldbOptions(create_if_missing=False, error_if_exists=False)
    reader = LEVELDB.Leveldb(db_path,options)

    def show():
        it = reader.get_iterater(reverse=False)
        i = 0
        for item in it:
            print(i,item)
            i += 1

    def test_find(key):
        value = reader.get(key)
        print('find', type(value), value)

    show()

    test_find(b'input_0')
    test_find(b'input_5')
    test_find(b'input_10')

    reader.close()

test_write(db_path)
test_read(db_path)