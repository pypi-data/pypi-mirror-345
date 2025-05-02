import base64
import struct
from typing import Any
import msgpack


def b2b64(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def b642b(data: str) -> bytes:
    return base64.b64decode(data)


def unpack_buffer_to_list(buffer, is_little, data_len, pack_unit_format) -> list[Any]:
    buffer = bytearray(buffer)
    buffer_len = len(buffer)
    nb_items = int(buffer_len / data_len)
    struct_format = "".join([pack_unit_format for _ in range(0, nb_items)])

    return list(struct.unpack(f"{'<' if is_little else' >'}{struct_format}", buffer))


def to_msgpack(buffer: bytearray or bytes) -> bytes:
    res = b""
    for c_val in buffer:
        res += msgpack.packb(int(c_val), use_bin_type=True)
    return res
