# -*- coding: utf-8 -*-
# @Time:  15:32
# @Author: tk
# @File：demo_arrow

from tfrecords.python.io.arrow import IPC_Writer,IPC_StreamReader,IPC_MemoryMappedFileReader,arrow

path_file = "d:/tmp/data.arrow"

def test_write():
    schema = arrow.schema([
        arrow.field('id', arrow.int32()),
        arrow.field('text', arrow.utf8())
    ])

    a = arrow.Int32Builder()
    a.AppendValues([0,1,4])
    a = a.Finish().Value()

    b = arrow.StringBuilder()
    b.AppendValues(["aaaa","你是谁","张三"])
    b = b.Finish().Value()

    table = arrow.Table.Make(schema = schema,arrays=[a,b])
    fs = IPC_Writer(path_file,schema,with_stream = True)
    fs.write_table(table)
    fs.close()



def test_read():
    fs = IPC_StreamReader(path_file)
    table = fs.read_all()
    fs.close()
    print(table)

    col = table.GetColumnByName('text')
    text_list = col.chunk(0)
    for i in range(text_list.length()):
        x = text_list.Value(i)
        print(type(x), x)




test_write()
test_read()

