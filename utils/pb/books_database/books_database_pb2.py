# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: utils/pb/books_database/books_database.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n,utils/pb/books_database/books_database.proto\x12\x0e\x62ooks_database\":\n\x08\x42ookInfo\x12\x0f\n\x07\x62ook_id\x18\x01 \x01(\t\x12\r\n\x05title\x18\x02 \x01(\t\x12\x0e\n\x06\x61uthor\x18\x03 \x01(\t\"\x1e\n\x0bReadRequest\x12\x0f\n\x07\x62ook_id\x18\x01 \x01(\t\">\n\x0cWriteRequest\x12\x0f\n\x07\x62ook_id\x18\x01 \x01(\t\x12\r\n\x05title\x18\x02 \x01(\t\x12\x0e\n\x06\x61uthor\x18\x03 \x01(\t\" \n\rWriteResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x32\x98\x01\n\rBooksDatabase\x12?\n\x04Read\x12\x1b.books_database.ReadRequest\x1a\x18.books_database.BookInfo\"\x00\x12\x46\n\x05Write\x12\x1c.books_database.WriteRequest\x1a\x1d.books_database.WriteResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'utils.pb.books_database.books_database_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_BOOKINFO']._serialized_start=64
  _globals['_BOOKINFO']._serialized_end=122
  _globals['_READREQUEST']._serialized_start=124
  _globals['_READREQUEST']._serialized_end=154
  _globals['_WRITEREQUEST']._serialized_start=156
  _globals['_WRITEREQUEST']._serialized_end=218
  _globals['_WRITERESPONSE']._serialized_start=220
  _globals['_WRITERESPONSE']._serialized_end=252
  _globals['_BOOKSDATABASE']._serialized_start=255
  _globals['_BOOKSDATABASE']._serialized_end=407
# @@protoc_insertion_point(module_scope)
