# Generated by the protocol buffer compiler.  DO NOT EDIT!

from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)



DESCRIPTOR = descriptor.FileDescriptor(
  name='ZKM.proto',
  package='zk',
  serialized_pb='\n\tZKM.proto\x12\x02zk\"?\n\x03ZKM\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x0c\n\x04hwid\x18\x02 \x01(\t\x12\x0c\n\x04type\x18\x03 \x01(\x05\x12\x0f\n\x07options\x18\x04 \x03(\tB\x19\n\x10org.gibsonsec.zkB\x05ZKObj')




_ZKM = descriptor.Descriptor(
  name='ZKM',
  full_name='zk.ZKM',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='key', full_name='zk.ZKM.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='hwid', full_name='zk.ZKM.hwid', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='type', full_name='zk.ZKM.type', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='options', full_name='zk.ZKM.options', index=3,
      number=4, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=17,
  serialized_end=80,
)

DESCRIPTOR.message_types_by_name['ZKM'] = _ZKM

class ZKM(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _ZKM
  
  # @@protoc_insertion_point(class_scope:zk.ZKM)

# @@protoc_insertion_point(module_scope)
