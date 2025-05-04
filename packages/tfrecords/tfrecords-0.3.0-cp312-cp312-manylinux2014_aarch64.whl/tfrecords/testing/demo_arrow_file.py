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


    fs = IPC_Writer(path_file,schema,with_stream = False)

    # table = arrow.Table.Make(schema=schema, arrays=[a, b])
    # fs.write_table(table)
    # fs.write_table(table)

    batch = arrow.RecordBatch.Make(schema = schema,num_rows = a.length() ,columns=[a,b])
    fs.write_record_batch(batch)
    fs.write_record_batch(batch)
    fs.close()


def test_read():

    fs = IPC_MemoryMappedFileReader(path_file)

    for i in range(fs.num_record_batches()):
        batch: arrow.RecordBatch = fs.read_batch(i)
        text_list = batch.GetColumnByName('text')
        print(i,batch.num_rows())
        for i in range(text_list.length()):
            x = text_list.Value(i)
            print(type(x), x)
    fs.close()


test_write()
test_read()