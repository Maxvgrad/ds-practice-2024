# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: suggestions.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11suggestions.proto\x12\x0bsuggestions\"6\n\x04\x42ook\x12\x0f\n\x07\x62ook_id\x18\x01 \x01(\t\x12\r\n\x05title\x18\x02 \x01(\t\x12\x0e\n\x06\x61uthor\x18\x03 \x01(\t\"J\n\x1c\x43\x61lculateSuggestionsResponse\x12*\n\x0fsuggested_books\x18\x01 \x03(\x0b\x32\x11.suggestions.Book\"\xa0\x04\n\x1b\x43\x61lculateSuggestionsRequest\x12\x1f\n\x04user\x18\x01 \x01(\x0b\x32\x11.suggestions.User\x12,\n\x0b\x63redit_card\x18\x02 \x01(\x0b\x32\x17.suggestions.CreditCard\x12\x14\n\x0cuser_comment\x18\x03 \x01(\t\x12 \n\x05items\x18\x04 \x03(\x0b\x32\x11.suggestions.Item\x12\x15\n\rdiscount_code\x18\x05 \x01(\t\x12\x17\n\x0fshipping_method\x18\x06 \x01(\t\x12\x14\n\x0cgift_message\x18\x07 \x01(\t\x12-\n\x0f\x62illing_address\x18\x08 \x01(\x0b\x32\x14.suggestions.Address\x12\x15\n\rgift_wrapping\x18\t \x01(\x08\x12%\n\x1dterms_and_conditions_accepted\x18\n \x01(\x08\x12 \n\x18notification_preferences\x18\x0b \x03(\t\x12#\n\x06\x64\x65vice\x18\x0c \x01(\x0b\x32\x13.suggestions.Device\x12%\n\x07\x62rowser\x18\r \x01(\x0b\x32\x14.suggestions.Browser\x12\x13\n\x0b\x61pp_version\x18\x0e \x01(\t\x12\x19\n\x11screen_resolution\x18\x0f \x01(\t\x12\x10\n\x08referrer\x18\x10 \x01(\t\x12\x17\n\x0f\x64\x65vice_language\x18\x11 \x01(\t\"%\n\x04User\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07\x63ontact\x18\x02 \x01(\t\"B\n\nCreditCard\x12\x0e\n\x06number\x18\x01 \x01(\t\x12\x17\n\x0f\x65xpiration_date\x18\x02 \x01(\t\x12\x0b\n\x03\x63vv\x18\x03 \x01(\t\"&\n\x04Item\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x10\n\x08quantity\x18\x02 \x01(\x05\"T\n\x07\x41\x64\x64ress\x12\x0e\n\x06street\x18\x01 \x01(\t\x12\x0c\n\x04\x63ity\x18\x02 \x01(\t\x12\r\n\x05state\x18\x03 \x01(\t\x12\x0b\n\x03zip\x18\x04 \x01(\t\x12\x0f\n\x07\x63ountry\x18\x05 \x01(\t\"1\n\x06\x44\x65vice\x12\x0c\n\x04type\x18\x01 \x01(\t\x12\r\n\x05model\x18\x02 \x01(\t\x12\n\n\x02os\x18\x03 \x01(\t\"(\n\x07\x42rowser\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07version\x18\x02 \x01(\t2\x81\x01\n\x12SuggestionsService\x12k\n\x14\x43\x61lculateSuggestions\x12(.suggestions.CalculateSuggestionsRequest\x1a).suggestions.CalculateSuggestionsResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'suggestions_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_BOOK']._serialized_start=34
  _globals['_BOOK']._serialized_end=88
  _globals['_CALCULATESUGGESTIONSRESPONSE']._serialized_start=90
  _globals['_CALCULATESUGGESTIONSRESPONSE']._serialized_end=164
  _globals['_CALCULATESUGGESTIONSREQUEST']._serialized_start=167
  _globals['_CALCULATESUGGESTIONSREQUEST']._serialized_end=711
  _globals['_USER']._serialized_start=713
  _globals['_USER']._serialized_end=750
  _globals['_CREDITCARD']._serialized_start=752
  _globals['_CREDITCARD']._serialized_end=818
  _globals['_ITEM']._serialized_start=820
  _globals['_ITEM']._serialized_end=858
  _globals['_ADDRESS']._serialized_start=860
  _globals['_ADDRESS']._serialized_end=944
  _globals['_DEVICE']._serialized_start=946
  _globals['_DEVICE']._serialized_end=995
  _globals['_BROWSER']._serialized_start=997
  _globals['_BROWSER']._serialized_end=1037
  _globals['_SUGGESTIONSSERVICE']._serialized_start=1040
  _globals['_SUGGESTIONSSERVICE']._serialized_end=1169
# @@protoc_insertion_point(module_scope)
