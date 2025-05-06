# type: ignore
from caterpillar.py import *

from impacket import tds

class VARCHAR(FieldStruct):
    def __init__(self, sub) -> None:
        super().__init__()
        self.struct = sub

    def unpack_single(self, context) -> str:
        size = self.struct.__unpack__(context)
        return context._io.read(size * 2).decode("utf-16le")

    def pack_single(self, obj, context) -> None:
        length = len(obj)
        self.struct.__pack__(length, context)
        context._io.write(obj.encode("utf-16le"))


class US_VARCHAR(VARCHAR):
    __struct__ = VARCHAR(uint16)


class B_VARCHAR(VARCHAR):
    __struct__ = VARCHAR(uint8)


@struct(order=LittleEndian)
class TDS_ERROR:
    token_type: uint8 = tds.TDS_ERROR_TOKEN
    length: uint16 = 0
    number: uint32
    state: uint8
    class_: uint8
    msg: US_VARCHAR
    server_name: B_VARCHAR
    process_name: B_VARCHAR
    line_number: uint16

    def length_hint(self) -> int:
        return (
            12
            + len(self.msg) * 2
            + len(self.server_name) * 2
            + len(self.process_name) * 2
        )


data = bytes.fromhex(
    "aa580018480000010e1d004c006f00670069006e0020006600610069006c0065006400200066006f0072002000750073006500720020002700750073006500720027002e0009440052004f00490044004c00410042003100000100"
)
error = unpack(TDS_ERROR, data)
print(error, error.length_hint())
error.length = error.length_hint()
assert pack(error) == data