# -*- coding: utf-8 -*-
# @Time    : 2022/9/8 15:49

import tfrecords
options = "SNAPPY"
def test_write(filename, N=3, context='aaa'):
    with tfrecords.TFRecordWriter(filename, options=options) as file_writer:
        batch_data = []
        for i in range(N):
            d = context + '____' + str(i)
            batch_data.append(d)
            if (i + 1) % 100 == 0:
                file_writer.write_batch(batch_data)
                batch_data.clear()
        if len(batch_data):
            file_writer.write_batch(batch_data)
            batch_data.clear()

def test_record_iterator(example_paths):
    print('test_record_iterator')
    for example_path in example_paths:
        iterator = tfrecords.tf_record_iterator(example_path, options=options, skip_bytes=0, with_share_memory=True)
        offset_list = iterator.read_offsets(0)
        count = iterator.read_count(0)
        print(count)
        num = 0
        for iter in iterator:
            num += 1
            print(iter)

def test_random_reader(example_paths):
    print('test_random_reader')
    for example_path in example_paths:
        file_reader = tfrecords.tf_record_random_reader(example_path, options=options, with_share_memory=True)
        last_pos = 0
        while True:
            try:
                x,pos = file_reader.read(last_pos)
                print(x,pos)
                last_pos = pos

            except Exception as e:
                break

def test_random_reader2(example_paths):
    print('test_random_reader2')
    for example_path in example_paths:
        file_reader = tfrecords.tf_record_random_reader(example_path, options=options, with_share_memory=True)
        skip_bytes = 0
        offset_list = file_reader.read_offsets(skip_bytes)
        for offset,length in offset_list:
            x, _ = file_reader.read(offset)
            print(x)

test_write('d:/tmp/example.tfrecords0',2,'file0')

example_paths = tfrecords.glob('d:/tmp/example.tfrecords*')
print(example_paths)
test_record_iterator(example_paths)
print()
test_random_reader(example_paths)
print()
test_random_reader2(example_paths)
print()