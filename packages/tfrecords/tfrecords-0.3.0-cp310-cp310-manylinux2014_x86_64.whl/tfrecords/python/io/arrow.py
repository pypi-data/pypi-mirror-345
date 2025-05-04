# -*- coding: utf-8 -*-
# @Time:  21:44
# @Author: tk
# @File：core
import inspect
import typing

from ...lib.arrow_lib import arrow,parquet


__all__ = [
    'arrow',
    'parquet',
    'IPC_MemoryMappedFileReader',
    'IPC_StreamReader',
    'IPC_Writer',
    'ParquetReader',
    'ParquetWriter'
]


def get_classes(arg):
    classes = []
    clsmembers = inspect.getmembers(arg, inspect.isclass)
    for (name, class_) in clsmembers:
        classes.append((name,class_))
    return classes

classes = get_classes(arrow) + get_classes(arrow.io) + get_classes(arrow.ipc)

for name_,class_ in classes:
    if getattr(class_, 'ToString', None) is not None and callable(class_.ToString):
        class_.__repr_old__ =  class_.__repr__
        class_.__repr__ = class_.ToString
        class_.__str__ = class_.ToString



def __ReaderProperties_repr(self: parquet.ReaderProperties):
    rstr =  f'parquet.ReaderProperties: \n' + \
            f'is_buffered_stream_enabled => {self.is_buffered_stream_enabled()} \n' + \
            f'buffer_size => {self.buffer_size()} \n' + \
            f'thrift_container_size_limit => {self.thrift_container_size_limit()} \n' + \
            f'thrift_string_size_limit => {self.thrift_string_size_limit()} \n' + \
            f'page_checksum_verification => {self.page_checksum_verification()} \n' + \
            f'memory_pool => {self.memory_pool()} \n'
    return rstr

def __WriterProperties_repr(self: parquet.WriterProperties):

    rstr = f'parquet.WriterProperties: \n' + \
           f'memory_pool => {self.memory_pool()} \n' + \
           f'data_page_version => {self.data_page_version()} \n' + \
           f'version => {self.version()} \n' + \
           f'created_by => {self.created_by()} \n' + \
           f'data_pagesize => {self.data_pagesize()} \n' + \
           f'store_decimal_as_integer => {self.store_decimal_as_integer()} \n' + \
           f'max_row_group_length => {self.max_row_group_length()} \n' + \
           f'write_batch_size => {self.write_batch_size()} \n' + \
           f'page_checksum_enabled => {self.page_checksum_enabled()} \n' + \
           f'write_page_index => {self.write_page_index()} \n' + \
           f'dictionary_index_encoding => {self.dictionary_index_encoding()} \n' + \
           f'dictionary_pagesize_limit => {self.dictionary_pagesize_limit()} \n' + \
           f'dictionary_page_encoding => {self.dictionary_page_encoding()} \n'
    return rstr

def __ArrowWriterProperties_repr(self: parquet.ArrowWriterProperties):
    rstr = f'parquet.ArrowWriterProperties: \n' + \
           f'use_threads => {self.use_threads()} \n' + \
           f'engine_version => {self.engine_version()} \n' + \
           f'coerce_timestamps_enabled => {self.coerce_timestamps_enabled()} \n' + \
           f'compliant_nested_types => {self.compliant_nested_types()} \n' + \
           f'store_schema => {self.store_schema()} \n' + \
           f'support_deprecated_int96_timestamps => {self.support_deprecated_int96_timestamps()} \n'
    return rstr


parquet.ReaderProperties.__repr__ = __ReaderProperties_repr
parquet.WriterProperties.__repr__ = __WriterProperties_repr
parquet.ArrowWriterProperties.__repr__ = __ArrowWriterProperties_repr

parquet.ReaderProperties.__str__ = __ReaderProperties_repr
parquet.WriterProperties.__str__ = __WriterProperties_repr
parquet.ArrowWriterProperties.__str__ = __ArrowWriterProperties_repr


def __IpcReadOptions_repr(self: arrow.ipc.IpcReadOptions):
    rstr =  f'parquet.IpcReadOptions: \n' + \
            f'max_recursion_depth => {self.max_recursion_depth} \n' + \
            f'memory_pool => {self.memory_pool} \n' + \
            f'included_fields => {self.included_fields} \n' + \
            f'use_threads => {self.use_threads} \n' + \
            f'pre_buffer_cache_options => {self.pre_buffer_cache_options} \n'
    return rstr


def __IpcWriteOptions_repr(self: arrow.ipc.IpcWriteOptions):
    rstr =  f'parquet.IpcWriteOptions: \n' + \
            f'allow_64bit => {self.allow_64bit} \n' + \
            f'max_recursion_depth => {self.max_recursion_depth} \n' + \
            f'alignment => {self.alignment} \n' + \
            f'write_legacy_ipc_format => {self.write_legacy_ipc_format} \n' + \
            f'codec => {self.codec} \n' + \
            f'min_space_savings => {self.min_space_savings} \n' + \
            f'use_threads => {self.use_threads} \n' + \
            f'emit_dictionary_deltas => {self.emit_dictionary_deltas} \n' + \
            f'unify_dictionaries => {self.unify_dictionaries} \n' + \
            f'metadata_version => {self.metadata_version} \n'
    return rstr

def __IpcCacheOptions_repr(self: arrow.ipc.CacheOptions):
    rstr =  f'arrow.ipc.CacheOptions: \n' + \
            f'hole_size_limit => {self.hole_size_limit} \n' + \
            f'range_size_limit => {self.range_size_limit} \n' + \
            f'lazy => {self.lazy} \n'
    return rstr


arrow.ipc.IpcReadOptions.__repr__ = __IpcReadOptions_repr
arrow.ipc.IpcWriteOptions.__repr__ = __IpcWriteOptions_repr
arrow.ipc.CacheOptions.__repr__ = __IpcCacheOptions_repr

arrow.ipc.IpcReadOptions.__str__ = __IpcReadOptions_repr
arrow.ipc.IpcWriteOptions.__str__ = __IpcWriteOptions_repr
arrow.ipc.CacheOptions.__str__ = __IpcCacheOptions_repr


def __Codecrepr(self: arrow.io.Codec):
    rstr =  f'arrow.io.Codec: \n' + \
            f'minimum_compression_level => {self.minimum_compression_level()} \n' + \
            f'maximum_compression_level => {self.maximum_compression_level()} \n' + \
            f'default_compression_level => {self.default_compression_level()} \n' + \
            f'compression_type => {self.compression_type()} \n' + \
            f'name => {self.name()} \n' + \
            f'compression_level => {self.compression_level()} \n'
    return rstr

arrow.io.Codec.__repr__ = __Codecrepr
arrow.io.Codec.__str__ = __Codecrepr









# UNCOMPRESSED,
# SNAPPY,
# GZIP,
# BROTLI,
# ZSTD,
# LZ4,
# LZ4_FRAME,
# LZO,
# BZ2,
# LZ4_HADOOP


def get_ipc_read_options(max_recursion_depth=64,
                         included_fields=None,
                         use_threads=None,
                         ensure_native_endian=None):

    options = arrow.ipc.IpcReadOptions.Defaults()
    if max_recursion_depth is not None:
        options.max_recursion_depth = max_recursion_depth

    if included_fields is not None:
        options.included_fields = included_fields

    if use_threads is not None:
        options.use_threads = use_threads

    if ensure_native_endian is not None:
        options.ensure_native_endian = ensure_native_endian

    return options

def get_ipc_write_options(default_options):
    options = arrow.ipc.IpcWriteOptions()
    if default_options.get('allow_64bit',None) is not None:
        options.allow_64bit = default_options['allow_64bit']
    if default_options.get('max_recursion_depth', None) is not None:
        options.max_recursion_depth = default_options['max_recursion_depth']
    if default_options.get('alignment', None) is not None:
        options.alignment = default_options['alignment']
    if default_options.get('write_legacy_ipc_format', None) is not None:
        options.write_legacy_ipc_format = default_options['write_legacy_ipc_format']
    if default_options.get('memory_pool', None) is not None:
        options.memory_pool = default_options['memory_pool']
    if default_options.get('codec', None) is not None:
        options.codec = default_options['codec']
    if default_options.get('min_space_savings', None) is not None:
        options.min_space_savings = default_options['min_space_savings']
    if default_options.get('use_threads',None) is not None:
        options.use_threads = default_options['use_threads']
    if default_options.get('emit_dictionary_deltas', None) is not None:
        options.emit_dictionary_deltas = default_options['emit_dictionary_deltas']
    if default_options.get('unify_dictionaries', None) is not None:
        options.unify_dictionaries = default_options['unify_dictionaries']
    if default_options.get('max_recursion_depth', None) is not None:
        options.max_recursion_depth = default_options['max_recursion_depth']
    if default_options.get('metadata_version', None) is not None:
        options.metadata_version = default_options['metadata_version']
    return options

class IPC_MemoryMappedFileReader:
    def __init__(self,filename,offset=None,length=None,file_mode=arrow.io.FileMode.READ,options: typing.Optional[typing.Dict] = None):
        if offset is not None and length is not None:
            self._sink = arrow.io.MemoryMappedFile.Open(path=filename, mode=file_mode,offset=offset,length=length).Value()
        else:
            self._sink = arrow.io.MemoryMappedFile.Open(path=filename,mode=file_mode).Value()

        default_options = dict(
            max_recursion_depth=64,
            included_fields=None,
            use_threads=None,
            ensure_native_endian=None
        )
        if options is not None:
            default_options.update(options)

        self._ipc_readoptions: arrow.ipc.IpcReadOptions =  get_ipc_read_options(**default_options)

        self._file_reader: arrow.RecordBatchReader = arrow.ipc.RecordBatchFileReader.Open(self._sink,options=self._ipc_readoptions).Value()

    def __del__(self):
        self.close()

    def schema(self):
        return self._file_reader.schema()

    def num_record_batches(self):
        return self._file_reader.num_record_batches()

    def version(self):
        return self._file_reader.version()

    def metadata(self):
        return self._file_reader.metadata()

    def read_batch(self,i):
        return self._file_reader.ReadRecordBatch(i).Value()

    def read_batch_with_metadata(self,i):
        return self._file_reader.ReadRecordBatchWithCustomMetadata(i).Value()

    def stats(self):
        return self._file_reader.stats()

    def count_rows(self):
        return self._file_reader.CountRows().Value()

    def pre_buffer_metadata(self,indices):
        self._file_reader.PreBufferMetadata(indices)
    def close(self):
        if self._sink is not None:
            self._sink.Close()
            self._sink = None

    def get_options(self):
        return self._ipc_readoptions

class IPC_StreamReader:
    def __init__(self,filename,options: typing.Optional[typing.Dict] = None):
        self._sink = arrow.io.ReadableFile.Open(filename).Value()

        default_options = dict(
            max_recursion_depth=64,
            included_fields=None,
            use_threads=None,
            ensure_native_endian=None
        )
        if options is not None:
            default_options.update(options)

        self._ipc_readoptions: arrow.ipc.IpcReadOptions = get_ipc_read_options(**default_options)

        self._file_reader: arrow.ipc.RecordBatchStreamReader = arrow.ipc.RecordBatchStreamReader.Open(self._sink,options=self._ipc_readoptions).Value()


    def __del__(self):
        self.close()

    def schema(self):
        return self._file_reader.schema()

    def next(self):
        batch = self._file_reader.Next().Value()
        return batch

    def read_all(self):
        table = self._file_reader.ReadAll().Value()
        return table

    def to_table(self):
        table = self._file_reader.ToTable().Value()
        return table

    def read_next(self):
        table = self._file_reader.ReadNext().Value()
        return table

    def read_all_batch(self):
        table = self._file_reader.ReadAllBatch().Value()
        return table

    def close(self):
        if self._file_reader is not None:
            self._file_reader.Close()
            self._file_reader = None

        if self._sink is not None:
            self._sink.Close()
            self._sink = None

    def get_options(self):
        return self._ipc_readoptions

class IPC_Writer:
    def __init__(self,filename,schema,with_stream = True,metadata = None,options = None):
        if metadata is not None and with_stream:
            raise ValueError('stream is not support metadata')

        metata_obj = None
        if metadata is not None and len(metadata) > 0:
            if not isinstance(metadata,dict):
                raise ValueError('espect metadata is dict')
            metata_obj = arrow.KeyValueMetadata()
            for k,v in metadata.items():
                assert isinstance(k,str) and isinstance(v,str)
                metata_obj.Append(k,v)


        default_options = dict(
            allow_64bit=False,
            max_recursion_depth=64,
            alignment=8,
            write_legacy_ipc_format = False,
            memory_pool = arrow.default_memory_pool(),
            codec=arrow.io.Codec.Create(arrow.io.Compression.ZSTD,arrow.io.Codec.UseDefaultCompressionLevel()).Value(),
            use_threads=True,
            emit_dictionary_deltas=False,
            unify_dictionaries=False,
            metadata_version=arrow.ipc.MetadataVersion.V5
        )
        if options is not None:
            default_options.update(options)

        self._options = get_ipc_write_options(default_options)
        self._sink = arrow.io.FileOutputStream.Open(filename).Value()
        if with_stream:
            self._file_writer: arrow.ipc.RecordBatchWriter = arrow.ipc.MakeStreamWriter(sink=self._sink,
                                                                                        schema=schema,
                                                                                        options=self._options).Value()
        else:
            self._file_writer: arrow.ipc.RecordBatchWriter = arrow.ipc.MakeFileWriter(sink=self._sink,
                                                                                      schema=schema,
                                                                                      options=self._options,
                                                                                      metadata=metata_obj).Value()

    def __del__(self):
        self.close()

    def get_options(self):
        return self._options



    def close(self):
        if self._file_writer is not None:
            self._file_writer.Close()
            self._file_writer = None

        if self._sink is not None:
            self._sink.Close()
            self._sink = None

    def write_table(self,table):
        status = self._file_writer.WriteTable(table)
        return status

    def write_record_batch(self,batch):
        status = self._file_writer.WriteRecordBatch(batch)
        return status











def get_arrow_writer_properties(enable_deprecated_int96_timestamps=True,
                                coerce_timestamps=None,
                                allow_truncated_timestamps = True,
                                store_schema = True,
                                enable_compliant_nested_types = True,
                                engine_version = parquet.ArrowWriterProperties.EngineVersion.V2,
                                use_threads=None):
    builder = parquet.ArrowWriterProperties.Builder()
    if enable_deprecated_int96_timestamps:
        builder = builder.enable_deprecated_int96_timestamps()
    else:
        builder = builder.disable_deprecated_int96_timestamps()
    if coerce_timestamps is not None:
        builder = builder.coerce_timestamps(coerce_timestamps)

    if allow_truncated_timestamps:
        builder = builder.allow_truncated_timestamps()
    else:
        builder = builder.disallow_truncated_timestamps()

    if store_schema:
        builder = builder.store_schema()

    if enable_compliant_nested_types:
        builder = builder.enable_compliant_nested_types()
    else:
        builder = builder.disable_compliant_nested_types()
    builder = builder.set_engine_version(engine_version)

    if use_threads is not None:
        builder = builder.set_use_threads(use_threads)
    properties = builder.build()
    return properties

def get_parquet_writer_properties(
    memory_pool,
    enable_dictionary = True,
    dictionary_pagesize_limit=None,
    write_batch_size=None,
    max_row_group_length=None,
    data_pagesize=None,
    data_page_version=None,
    version=None,
    created_by=None,
    enable_page_checksum=None,
    encoding=None,
    compression=None,
    compression_level = None,
    max_statistics_size = None,
    encryption = None,
    enable_statistics = True,
    enable_store_decimal_as_integer = True,
    enable_write_page_index = True
):
    builder = parquet.WriterProperties.Builder()
    if memory_pool is not None:
        builder = builder.memory_pool(memory_pool)

    if enable_dictionary:
        builder = builder.enable_dictionary()
    else:
        builder = builder.disable_dictionary()

    if dictionary_pagesize_limit is not None:
        builder = builder.dictionary_pagesize_limit(dictionary_pagesize_limit)

    if write_batch_size is not None:
        builder = builder.write_batch_size(write_batch_size)

    if max_row_group_length is not None:
        builder = builder.max_row_group_length(max_row_group_length)

    if data_pagesize is not None:
        builder = builder.data_pagesize(data_pagesize)

    if data_page_version is not None:
        builder = builder.data_page_version(data_page_version)

    if version is not None:
        builder = builder.data_page_version(version)

    if created_by is not None:
        builder = builder.data_page_version(created_by)

    if enable_page_checksum is not None:
        builder = builder.enable_page_checksum()
    else:
        builder = builder.disable_page_checksum()

    if encoding is not None:
        builder = builder.encoding(encoding)

    if compression is not None:
        builder = builder.compression(compression)

    if compression_level is not None:
        builder = builder.compression_level(compression_level)

    if max_statistics_size is not None:
        builder = builder.max_statistics_size(max_statistics_size)

    if encryption is not None:
        raise not NotImplemented

    if enable_statistics:
        builder = builder.enable_statistics()
    else:
        builder = builder.disable_statistics()

    if enable_store_decimal_as_integer:
        builder = builder.enable_store_decimal_as_integer()
    else:
        builder = builder.disable_store_decimal_as_integer()

    if enable_write_page_index:
        builder = builder.enable_write_page_index()
    else:
        builder = builder.disable_write_page_index()

    properties = builder.build()
    return properties





class ParquetReader:
    def __init__(self,filename,memory_map=True,metadata = None,options = None):
        default_options = dict(enable_buffered_stream=None,
                          buffer_size= None,
                          thrift_string_size_limit= None,
                          file_decryption_properties= None,
                          check_crc= None)
        if options is not None:
            default_options.update(options)
        self._properties = self._parse_properties(**default_options)
        builder = parquet.FileReaderBuilder()
        self._sink = arrow.io.ReadableFile.Open(filename).Value()
        # status = builder.Open(file=self._sink,properties=self.properties)
        status = builder.OpenFile(filename,memory_map=memory_map,properties=self._properties,metadata=metadata)
        assert status.ok(),status.message()
        self._file_reader: parquet.FileReader = builder.memory_pool(arrow.default_memory_pool()).Build().Value()

    def _parse_properties(self,
                          enable_buffered_stream= None,
                          buffer_size = None,
                          thrift_string_size_limit = None,
                          file_decryption_properties = None,
                          check_crc= None
                          ):

        properties = parquet.ReaderProperties()
        if enable_buffered_stream is not None:
            if enable_buffered_stream:
                properties.enable_buffered_stream()
            else:
                properties.disable_buffered_stream()
        if buffer_size:
            properties.set_buffer_size(buffer_size)
        if thrift_string_size_limit:
            properties.set_thrift_string_size_limit(thrift_string_size_limit)
        if file_decryption_properties is not None:
            raise ValueError('no support for file_decryption_properties ')
        if check_crc:
            properties.set_page_checksum_verification(check_crc)
        return properties

    def __del__(self):
        self.close()

    def close(self):
        if self._sink is not None:
            self._sink.Close()
            self._sink = None

    def get_column(self,i):
        return self._file_reader.GetColumn(i)

    def get_schema(self):
        return self._file_reader.GetSchema()

    def read_column(self,i):
        return self._file_reader.ReadColumn(i)

    def get_batch_reader(self,row_group_indices=None,column_indices=None):
        if row_group_indices is not None and column_indices is not None:
            return self._file_reader.GetRecordBatchReader(row_group_indices,column_indices)
        elif row_group_indices is not None:
            return self._file_reader.GetRecordBatchReader(row_group_indices)
        return self._file_reader.GetRecordBatchReader()

    def read_table(self,column_indices=None)-> typing.Union[arrow.Table,typing.Any]:
        if column_indices is not None:
            return self._file_reader.ReadTable(column_indices).Value()
        return self._file_reader.ReadTable().Value()

    def read_row_group(self , i,column_indices = None)-> typing.Union[parquet.RowGroupReader,typing.Any]:
        if column_indices is not None:
            return self._file_reader.ReadRowGroup(i,column_indices).Value()
        return self._file_reader.ReadRowGroup(i).Value()

    def read_row_groups(self , row_groups,column_indices = None)-> typing.Union[parquet.RowGroupReader,typing.Any]:
        if column_indices is not None:
            return self._file_reader.ReadRowGroups(row_groups,column_indices).Value()
        return self._file_reader.ReadRowGroups(row_groups).Value()

    def scan_contents(self, columns, column_batch_size):
        return self._file_reader.ScanContents(columns,column_batch_size).Value()

    def row_group(self, row_group_index) -> typing.Union[parquet.RowGroupReader,typing.Any]:
        return self._file_reader.RowGroup(row_group_index)

    def num_row_groups(self) -> int:
        return self._file_reader.num_row_groups()

    def parquet_reader(self) -> typing.Union[parquet.ParquetFileReader,typing.Any]:
        return self._file_reader.parquet_reader()

    def set_use_threads(self,use_threads):
        return self._file_reader.set_use_threads(use_threads)

    def set_batch_size(self,batch_size):
        return self._file_reader.set_batch_size(batch_size)

    def properties(self)  -> typing.Union[parquet.ReaderProperties,typing.Any]:
        return self._file_reader.properties()


class ParquetWriter:
    def __init__(self,
                 filename,
                 schema,
                 parquet_options=None,
                 arrow_options=None):

        self._schema = schema

        default_arrow_options = dict(
            enable_deprecated_int96_timestamps=True,
            coerce_timestamps=None,
            allow_truncated_timestamps=True,
            store_schema=True,
            enable_compliant_nested_types=True,
            engine_version=parquet.ArrowWriterProperties.EngineVersion.V2,
            use_threads=None)

        codec = arrow.io.Codec.Create(arrow.io.Compression.SNAPPY).Value()
        default_parquet_options = dict(
            memory_pool=arrow.default_memory_pool(),
            enable_dictionary=True,
            dictionary_pagesize_limit=None,
            write_batch_size=None,
            max_row_group_length=None,
            data_pagesize=None,
            data_page_version=None,
            version=None,
            created_by=None,
            enable_page_checksum=None,
            encoding=None,
            compression=codec.compression_type(),
            compression_level=codec.compression_level(),
            max_statistics_size=None,
            encryption=None,
            enable_statistics=True,
            enable_store_decimal_as_integer=True,
            enable_write_page_index=True
        )
        if arrow_options is not None:
            default_arrow_options.update(arrow_options)

        if parquet_options is not None:
            default_parquet_options.update(parquet_options)

        self._arrow_properties = get_arrow_writer_properties(**default_arrow_options)
        self._properties = get_parquet_writer_properties(**default_parquet_options)

        self._sink = arrow.io.FileOutputStream.Open(filename).Value()
        self._file_writer: parquet.FileWriter = parquet.FileWriter.Open(schema=self._schema,
                                                                        pool=arrow.default_memory_pool(),
                                                                        sink=self._sink,
                                                                        properties=self._properties,
                                                                        arrow_properties=self._arrow_properties
                                                                        ).Value()




    def __del__(self):
        self.close()

    def close(self):
        if self._file_writer is not None:
            self._file_writer.Close()

        if self._sink is not None:
            self._sink.Close()
            self._sink = None

    def schema(self):
        return self._file_writer.schema()


    def write_table(self,table,chunk_size=1024 * 1024):
        status = self._file_writer.WriteTable(table,chunk_size=chunk_size)
        return status

    def new_row_group(self,chunk_size):
        status = self._file_writer.NewRowGroup(chunk_size)
        return status


    def write_column_chunk(self,data):
        status = self._file_writer.WriteColumnChunk(data)
        return status

    def new_buffered_row_group(self):
        status = self._file_writer.NewBufferedRowGroup()
        return status

    def write_record_batch(self,batch):
        status = self._file_writer.WriteRecordBatch(batch)
        return status