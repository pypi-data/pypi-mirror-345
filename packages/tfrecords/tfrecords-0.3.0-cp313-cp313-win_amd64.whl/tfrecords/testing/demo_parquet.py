# -*- coding: utf-8 -*-
# @Time:  15:28
# @Author: tk
# @File：demo_arrow

from tfrecords.python.io.arrow import ParquetWriter,IPC_StreamReader,ParquetReader,arrow
path_file = "d:/tmp/data.parquet"

def test_write():
    schema = arrow.schema([
        arrow.field('id', arrow.int32()),
        arrow.field('text', arrow.utf8())
    ])

    a = arrow.Int32Builder()
    a.AppendValues([0, 1, 4, 5])
    a = a.Finish().Value()

    b = arrow.StringBuilder()
    b.AppendValues(["aaaa", "你是谁", "张三", "李赛"])
    b = b.Finish().Value()

    table = arrow.Table.Make(schema=schema, arrays=[a, b])

    fs = ParquetWriter(path_file, schema)
    fs.write_table(table)
    fs.close()

def test_read():

    fs = ParquetReader(path_file,options=dict(buffer_size=2))
    table = fs.read_table()
    fs.close()
    table = table.Flatten().Value()
    print(table)

    col = table.GetColumnByName('text')
    text_list = col.chunk(0)
    for i in range(text_list.length()):
        x = text_list.Value(i)
        print(type(x),x)


test_write()
test_read()