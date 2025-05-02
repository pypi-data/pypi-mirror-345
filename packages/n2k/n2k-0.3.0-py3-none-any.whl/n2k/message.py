# N2kMsg.h
from __future__ import annotations

import struct
from binascii import hexlify
from typing import TYPE_CHECKING

from n2k import constants
from n2k.n2k import PGN
from n2k.utils import IntRef, clamp_int, millis

if TYPE_CHECKING:
    from n2k.stream import Stream


# WARNING: The round method employed by python differs from the one written in the ported C code
#  However this is the correct method for IEEE floating point numbers
#  https://en.wikipedia.org/wiki/Rounding#Round_half_to_even
class Message:
    # subclassed for each pgn; maybe use typed & named tuple or something else instead?
    max_data_len: int = 223
    priority: int
    pgn: int = 0  # unsigned long: 4 bytes
    source: int
    destination: int
    data: bytearray
    data_len: int
    msg_time: int = 0
    # ISO Multi Packet Support
    # tp_message: bool

    def __init__(
        self,
        source: int = 15,
        priority: int = 6,
        pgn: int = 0,
        data: bytearray | None = None,
    ) -> None:
        self.source = source
        self.destination = 255
        self.priority = priority & 0x7
        self.pgn = pgn
        self.msg_time = millis()
        if data is None:
            data = bytearray()
        self.data = data[: self.max_data_len]
        self.data_len = len(data)
        # self.tp_message = False

    def __repr__(self) -> str:
        s = "Message("
        s += "source=" + str(self.source) + ","
        s += "destination=" + str(self.destination) + ","
        s += "priority=" + str(self.priority) + ","

        pgn = self.pgn
        try:
            pgn = PGN(pgn)
        except ValueError:
            pass

        s += "pgn=" + str(pgn) + ","
        s += "msg_time=" + str(self.msg_time) + ","
        s += "data=" + str(hexlify(self.data, sep=" ")) + ","
        s += "data_len=" + str(self.data_len) + ","
        return s

    def check_destination(self) -> None:
        """
        Verify the destination, as only PGNs where the lower byte is 0 can be sent to specific addresses.
        :return:
        """
        if self.pgn & 0xFF != 0:
            # set destination to broadcast
            self.destination = 0xFF

    def is_valid(self) -> bool:
        return self.pgn != 0 and len(self.data) > 0

    def get_remaining_data_length(self, index: int) -> int:
        if len(self.data) > index:
            return len(self.data) - index
        return 0

    def get_available_data_length(self) -> int:
        return max(0, self.max_data_len - len(self.data))

    # Data Insertion
    def add_float(self, v: float, undef_val: float = constants.N2K_FLOAT_NA) -> None:
        """
        Store :obj:`float` values as single precision IEEE floating point

        :param v: value to be stored
        :param undef_val: value which marks the field as undefined, defaults to :py:obj:`constants.N2K_FLOAT_NA`
        """
        if v != undef_val:
            self.data.extend(struct.pack("<f", v))
        else:
            self.data.extend(struct.pack("<i", constants.N2K_INT32_NA))
        self.data_len += 4

    def add_1_byte_udouble(
        self,
        v: float,
        precision: float,
        undef_val: float = constants.N2K_DOUBLE_NA,
    ) -> None:
        """
        Store :obj:`float` values with a fixed amount of decimal places

        Limited to 1 byte (0 - 254) unsigned integer values. Thus if we choose a precision of 0.1, the maximum that could be stored is 0.1 * 254 = 25.4
        If the value is outside of this range, it will be clamped to 0 or 254.
        255 is used to mark the field as undefined.

        :param v: value to be stored
        :param precision: factor by which the value is divided before being rounded and stored
        :param undef_val: value which marks the field as undefined, defaults to :py:obj:`constants.N2K_DOUBLE_NA`
        """
        if v != undef_val:
            v = clamp_int(0, round(v / precision), constants.N2K_UINT8_OR)
            self.data.extend(struct.pack("<B", v))
        else:
            self.data.extend(struct.pack("<B", constants.N2K_UINT8_NA))
        self.data_len += 1

    def add_1_byte_double(
        self,
        v: float,
        precision: float,
        undef_val: float = constants.N2K_DOUBLE_NA,
    ) -> None:
        """
        Store :obj:`float` values with a fixed amount of decimal places

        Limited to 1 byte (-128 - 126) signed integer values. Thus if we choose a precision of 0.1, the maximum that could be stored is 0.1 * 126 = 12.6
        If the value is outside of this range, it will be clamped to -128 or 126.
        127 is used to mark the field as undefined.

        :param v: value to be stored
        :param precision: factor by which the value is divided before being rounded and stored
        :param undef_val: value which marks the field as undefined, defaults to :py:obj:`constants.N2K_DOUBLE_NA`
        """
        if v != undef_val:
            v = clamp_int(
                constants.N2K_INT8_MIN,
                round(v / precision),
                constants.N2K_INT8_OR,
            )
            self.data.extend(struct.pack("<b", v))
        else:
            self.data.extend(struct.pack("<b", constants.N2K_INT8_NA))
        self.data_len += 1

    def add_2_byte_udouble(
        self,
        v: float,
        precision: float,
        undef_val: float = constants.N2K_DOUBLE_NA,
    ) -> None:
        """
        Store :obj:`float` values with a fixed amount of decimal places

        Limited to 2 bytes (0 - 65534) unsigned integer values. Thus if we choose a precision of 0.01, the maximum that could be stored is 0.01 * 65534 = 655.34
        If the value is outside of this range, it will be clamped to 0 or 65534.
        65535 is used to mark the field as undefined.

        :param v: value to be stored
        :param precision: factor by which the value is divided before being rounded and stored
        :param undef_val: value which marks the field as undefined, defaults to :py:obj:`constants.N2K_DOUBLE_NA`
        """
        if v != undef_val:
            v = clamp_int(0, round(v / precision), constants.N2K_UINT16_OR)
            self.data.extend(struct.pack("<H", v))
        else:
            self.data.extend(struct.pack("<H", constants.N2K_UINT16_NA))
        self.data_len += 2

    def add_2_byte_double(
        self,
        v: float,
        precision: float,
        undef_val: float = constants.N2K_DOUBLE_NA,
    ) -> None:
        """
        Store :obj:`float` values with a fixed amount of decimal places

        Limited to 2 bytes (-32768 - 32676) signed integer values. Thus if we choose a precision of 0.01, the maximum that could be stored is 0.01 * 32676 = 326.76
        If the value is outside of this range, it will be clamped to -32768 or 32676.
        32767 is used to mark the field as undefined.

        :param v: value to be stored
        :param precision: factor by which the value is divided before being rounded and stored
        :param undef_val: value which marks the field as undefined, defaults to :py:obj:`constants.N2K_DOUBLE_NA`
        """
        if v != undef_val:
            v = clamp_int(
                constants.N2K_INT16_MIN,
                round(v / precision),
                constants.N2K_INT16_OR,
            )
            self.data.extend(struct.pack("<h", v))
        else:
            self.data.extend(struct.pack("<h", constants.N2K_INT16_NA))
        self.data_len += 2

    def add_3_byte_udouble(
        self,
        v: float,
        precision: float,
        undef_val: float = constants.N2K_DOUBLE_NA,
    ) -> None:
        """
        Store :obj:`float` values with a fixed amount of decimal places

        Limited to 3 bytes (0 - 16777214) unsigned integer values. Thus if we choose a precision of 0.001, the maximum that could be stored is 0.001 * 16777214 = 16777.214
        If the value is outside of this range, it will be clamped to 0 or 16777214.
        16777215 is used to mark the field as undefined.

        :param v: value to be stored
        :param precision: factor by which the value is divided before being rounded and stored
        :param undef_val: value which marks the field as undefined, defaults to :py:obj:`constants.N2K_DOUBLE_NA`
        """
        if v != undef_val:
            v = clamp_int(0, round(v / precision), constants.N2K_UINT24_OR)
            self.data.extend(struct.pack("<I", v)[:3])
        else:
            self.data.extend(struct.pack("<I", constants.N2K_UINT24_NA)[:3])
        self.data_len += 3

    def add_3_byte_double(
        self,
        v: float,
        precision: float,
        undef_val: float = constants.N2K_DOUBLE_NA,
    ) -> None:
        """
        Store :obj:`float` values with a fixed amount of decimal places

        Limited to 3 bytes (-8388608 - 8388606) signed integer values. Thus if we choose a precision of 0.001, the maximum that could be stored is 0.001 * 8388606 = 8388.606
        If the value is outside of this range, it will be clamped to -8388608 or 8388606.
        8388607 is used to mark the field as undefined.

        :param v: value to be stored
        :param precision: factor by which the value is divided before being rounded and stored
        :param undef_val: value which marks the field as undefined, defaults to :py:obj:`constants.N2K_DOUBLE_NA`
        """
        if v != undef_val:
            v = clamp_int(
                constants.N2K_INT24_MIN,
                round(v / precision),
                constants.N2K_INT24_OR,
            )
            self.data.extend(v.to_bytes(3, byteorder="little", signed=True))
        else:
            self.data.extend(struct.pack("<i", constants.N2K_INT24_NA)[:3])
        self.data_len += 3

    def add_4_byte_udouble(
        self,
        v: float,
        precision: float,
        undef_val: float = constants.N2K_DOUBLE_NA,
    ) -> None:
        """
        Store :obj:`float` values with a fixed amount of decimal places

        Limited to 4 bytes (0 - 4294967294) unsigned integer values. Thus if we choose a precision of 0.00001, the maximum that could be stored is 0.00001 * 4294967294 = 42949.67294
        If the value is outside of this range, it will be clamped to 0 or 4294967294.
        4294967295 is used to mark the field as undefined.

        :param v: value to be stored
        :param precision: factor by which the value is divided before being rounded and stored
        :param undef_val: value which marks the field as undefined, defaults to :py:obj:`constants.N2K_DOUBLE_NA`
        """
        if v != undef_val:
            v = clamp_int(0, round(v / precision), constants.N2K_UINT32_OR)
            self.data.extend(struct.pack("<I", v))
        else:
            self.data.extend(struct.pack("<I", constants.N2K_UINT32_NA))
        self.data_len += 4

    def add_4_byte_double(
        self,
        v: float,
        precision: float,
        undef_val: float = constants.N2K_DOUBLE_NA,
    ) -> None:
        """
        Store :obj:`float` values with a fixed amount of decimal places

        Limited to 4 bytes (-2147483648 - 2147483646) signed integer values. Thus if we choose a precision of 0.00001, the maximum that could be stored is 0.00001 * 2147483646 = 21474.83646
        If the value is outside of this range, it will be clamped to -2147483648 or 2147483646.
        2147483647 is used to mark the field as undefined.

        :param v: value to be stored
        :param precision: factor by which the value is divided before being rounded and stored
        :param undef_val: value which marks the field as undefined, defaults to :py:obj:`constants.N2K_DOUBLE_NA`
        """
        if v != undef_val:
            v = clamp_int(
                constants.N2K_INT32_MIN,
                round(v / precision),
                constants.N2K_INT32_OR,
            )
            self.data.extend(struct.pack("<i", v))
        else:
            self.data.extend(struct.pack("<i", constants.N2K_INT32_NA))
        self.data_len += 4

    def add_8_byte_double(
        self,
        v: float,
        precision: float,
        undef_val: float = constants.N2K_DOUBLE_NA,
    ) -> None:
        """
        Store :obj:`float` values with a fixed amount of decimal places

        Limited to 8 bytes (-2^63 to 2^63-2) signed integer values. Thus if we choose a precision of 1e-7, the maximum that could be stored is 0.0000001 * (2^63-2).
        If the value is outside of this range, it will be clamped to -2^63 or 2^63-2.
        2^63-1 is used to mark the field as undefined.

        :param v: value to be stored
        :param precision: factor by which the value is divided before being rounded and stored
        :param undef_val: value which marks the field as undefined, defaults to :py:obj:`constants.N2K_DOUBLE_NA`
        """
        if v != undef_val:
            self.data.extend(struct.pack("<q", round(v / precision)))
        else:
            self.data.extend(struct.pack("<q", constants.N2K_INT64_NA))
        self.data_len += 8

    def add_byte_uint(self, v: int) -> None:
        self.data.extend(struct.pack("<B", v))
        self.data_len += 1

    def add_byte_int(self, v: int) -> None:
        self.data.extend(struct.pack("<b", v))
        self.data_len += 1

    def add_2_byte_uint(self, v: int) -> None:
        self.data.extend(struct.pack("<H", v))
        self.data_len += 2

    def add_2_byte_int(self, v: int) -> None:
        self.data.extend(struct.pack("<h", v))
        self.data_len += 2

    def add_3_byte_uint(self, v: int) -> None:
        self.data.extend(struct.pack("<I", v)[:3])
        self.data_len += 3

    def add_3_byte_int(self, v: int) -> None:
        self.data.extend(v.to_bytes(3, byteorder="little", signed=True))
        self.data_len += 3

    def add_4_byte_uint(self, v: int) -> None:
        self.data.extend(struct.pack("<I", v))
        self.data_len += 4

    def add_uint_64(self, v: int) -> None:
        self.data.extend(struct.pack("<Q", v))
        self.data_len += 8

    def add_str(self, v: str, length: int) -> None:
        encoded = v.encode("utf-8")[:length]
        for b in encoded:
            self.add_byte_uint(b)
        # fill up to length using 0xff. Garmin instead uses 0x00 to fill but both seems to work.
        for _b in range(length - len(encoded)):
            self.add_byte_uint(constants.STR_NULL_CHAR)

    def add_var_str(self, v: str) -> None:
        self.add_byte_uint(len(v) + 2)
        self.add_byte_uint(1)
        self.add_str(v, len(v))

    # make sure characters fall into range defined in table 14: 32-95 in ASCII
    # https://www.itu.int/dms_pubrec/itu-r/rec/m/R-REC-M.1371-1-200108-S!!PDF-E.pdf (Page 42)
    def add_ais_str(self, v: str, length: int) -> None:
        encoded = v.upper().encode("ascii")[:length]
        ascii_min = 32
        ascii_max = 95
        validated = [c if ascii_min <= c <= ascii_max else ord("?") for c in encoded]
        for b in validated:
            self.add_byte_uint(b)
        for _b in range(length - len(validated)):
            self.add_byte_uint(ord("@"))  # '@' is the AIS null character

    # Data Retrieval
    def get_float(
        self,
        index: IntRef,
        default: float = constants.N2K_FLOAT_NA,
    ) -> float:
        length = 4
        if index.value + length > self.data_len:
            return default
        if (
            struct.unpack("<i", self.data[index.value : index.value + length])[0]
            == constants.N2K_INT32_NA
        ):
            index.value += length
            return default
        v = struct.unpack("<f", self.data[index.value : index.value + length])[0]
        index.value += length
        return v

    def get_1_byte_udouble(
        self,
        precision: float,
        index: IntRef,
        default: float = constants.N2K_DOUBLE_NA,
    ) -> float:
        v = self.get_byte_uint(index)
        if v == constants.N2K_UINT8_NA:
            return default
        return apply_precision(v, precision)

    def get_1_byte_double(
        self,
        precision: float,
        index: IntRef,
        default: float = constants.N2K_DOUBLE_NA,
    ) -> float:
        v = self.get_byte_int(index)
        if v == constants.N2K_INT8_NA:
            return default
        return apply_precision(v, precision)

    def get_2_byte_udouble(
        self,
        precision: float,
        index: IntRef,
        default: float = constants.N2K_DOUBLE_NA,
    ) -> float:
        v = self.get_2_byte_uint(index)
        if v == constants.N2K_UINT16_NA:
            return default
        return apply_precision(v, precision)

    def get_2_byte_double(
        self,
        precision: float,
        index: IntRef,
        default: float = constants.N2K_DOUBLE_NA,
    ) -> float:
        v = self.get_2_byte_int(index)
        if v == constants.N2K_INT16_NA:
            return default
        return apply_precision(v, precision)

    def get_3_byte_udouble(
        self,
        precision: float,
        index: IntRef,
        default: float = constants.N2K_DOUBLE_NA,
    ) -> float:
        v = self.get_3_byte_uint(index)
        if v == constants.N2K_UINT24_NA:
            return default
        return apply_precision(v, precision)

    def get_3_byte_double(
        self,
        precision: float,
        index: IntRef,
        default: float = constants.N2K_DOUBLE_NA,
    ) -> float:
        v = self.get_3_byte_int(index)
        if v == constants.N2K_INT24_NA:
            return default
        return apply_precision(v, precision)

    def get_4_byte_udouble(
        self,
        precision: float,
        index: IntRef,
        default: float = constants.N2K_DOUBLE_NA,
    ) -> float:
        v = self.get_4_byte_uint(index)
        if v == constants.N2K_UINT32_NA:
            return default
        return apply_precision(v, precision)

    def get_4_byte_double(
        self,
        precision: float,
        index: IntRef,
        default: float = constants.N2K_DOUBLE_NA,
    ) -> float:
        v = self.get_4_byte_int(index)
        if v == constants.N2K_INT32_NA:
            return default
        return apply_precision(v, precision)

    def get_8_byte_double(
        self,
        precision: float,
        index: IntRef,
        default: float = constants.N2K_DOUBLE_NA,
    ) -> float:
        v = self.get_8_byte_int(index)
        if v == constants.N2K_INT64_NA:
            return default
        return apply_precision(v, precision)

    def get_byte_uint(self, index: IntRef) -> int:
        length = 1
        if index.value + length > self.data_len:
            return constants.N2K_UINT8_NA
        v = struct.unpack("<B", self.data[index.value : index.value + length])[0]
        index.value += length
        return v

    def get_byte_int(self, index: IntRef) -> int:
        length = 1
        if index.value + length > self.data_len:
            return constants.N2K_INT8_NA
        v = struct.unpack("<b", self.data[index.value : index.value + length])[0]
        index.value += length
        return v

    def get_2_byte_uint(
        self,
        index: IntRef,
        default: int = constants.N2K_UINT16_NA,
    ) -> int:
        length = 2
        if index.value + length > self.data_len:
            return default
        v = struct.unpack("<H", self.data[index.value : index.value + length])[0]
        index.value += length
        return v

    def get_2_byte_int(
        self,
        index: IntRef,
        default: int = constants.N2K_INT16_NA,
    ) -> int:
        length = 2
        if index.value + length > self.data_len:
            return default
        v = struct.unpack("<h", self.data[index.value : index.value + length])[0]
        index.value += length
        return v

    def get_3_byte_uint(
        self,
        index: IntRef,
        default: int = constants.N2K_UINT24_NA,
    ) -> int:
        length = 3
        if index.value + length > self.data_len:
            return default
        v = struct.unpack(
            "<I",
            self.data[index.value : index.value + length] + b"\x00",
        )[0]
        index.value += length
        return v

    def get_3_byte_int(
        self,
        index: IntRef,
        default: int = constants.N2K_INT24_NA,
    ) -> int:
        length = 3
        if index.value + length > self.data_len:
            return default
        v = int.from_bytes(
            self.data[index.value : index.value + length],
            byteorder="little",
            signed=True,
        )
        index.value += length
        return v

    def get_4_byte_uint(
        self,
        index: IntRef,
        default: int = constants.N2K_UINT32_NA,
    ) -> int:
        length = 4
        if index.value + length > self.data_len:
            return default
        v = struct.unpack("<I", self.data[index.value : index.value + length])[0]
        index.value += length
        return v

    def get_4_byte_int(
        self,
        index: IntRef,
        default: int = constants.N2K_UINT32_NA,
    ) -> int:
        length = 4
        if index.value + length > self.data_len:
            return default
        v = struct.unpack("<i", self.data[index.value : index.value + length])[0]
        index.value += length
        return v

    def get_uint_64(self, index: IntRef, default: int = constants.N2K_UINT64_NA) -> int:
        length = 8
        if index.value + length > self.data_len:
            return default
        v = struct.unpack("<Q", self.data[index.value : index.value + length])[0]
        index.value += length
        return v

    def get_8_byte_int(
        self,
        index: IntRef,
        default: int = constants.N2K_INT64_NA,
    ) -> int:
        length = 8
        if index.value + length > self.data_len:
            return default
        v = struct.unpack("<q", self.data[index.value : index.value + length])[0]
        index.value += length
        return v

    def get_str(self, length: int, index: IntRef, nul_char: bytes = b"@") -> str:
        # TODO: original function fills the end of the buffer (that the string is copied to) with zeros
        #  or at least with 2 zeros, depending on version
        ret = bytearray()
        if index.value + length > self.data_len:
            return ret.decode("utf-8")
        i = -1
        for i in range(length):
            b = self.get_byte_uint(index)
            if b in (0x00, constants.STR_NULL_CHAR, ord(nul_char)):
                # either null terminator or custom nul char (e.g. '@' for AIS)
                break
            ret.append(b)
        # ensure that the index gets advanced to correct amount, even if we find the null byte early
        index.value += length - (i + 1)
        return ret.decode("utf-8")

    def get_var_str(self, index: IntRef) -> str | None:
        length = self.get_byte_uint(index) - 2
        if length < 0:
            return None  # invalid length
        str_type = self.get_byte_uint(index)
        if str_type != 0x01:
            return None
        return self.get_str(length, index, b"\xff")

    # Data Manipulation
    def set_byte_uint(self, v: int, index: IntRef) -> bool:
        if index.value < self.data_len:
            self.data[index.value] = struct.pack("<B", v)[0]
            index.value += 1
            return True
        return False

    def set_2_byte_uint(self, v: int, index: IntRef) -> bool:
        if index.value + 1 < self.data_len:
            self.data[index.value : index.value + 1] = struct.pack("<H", v)[0:1]
            index.value += 2
            return True
        return False


# TODO: change all the set functions to instead subclass n2k.message and be the constructor of the
#  corresponding subclass?
#  Or maybe just be class functions? Or static functions that return a message (probably best)


def print_buf(port: Stream, length: int, p_data: str, add_lf: bool = False) -> None:
    print("NotImplemented print_buf")


def apply_precision(raw_value: int, precision: float) -> float:
    """
    Apply the precision to the raw value.

    Due to limitations of floating point numbers (https://docs.python.org/3/tutorial/floatingpoint.html) the exact value of many decimal numbers cannot be represented.
    When dividing by a float, python seems to return the actual number that the binary representation maps to.
    This is not a problem, but throws off unit tests that check for equality.
    Dividing by the inverse of the precision (which should always be an integer) instead, seems to yield the expected result.

    :param raw_value: value as parsed from the message
    :param precision: precision with which the value was stored
    :return: value with applied precision, with the appropriate number of decimal places
    """
    if precision > 1:
        return raw_value * precision
    inverse_precision = round(1 / precision)
    return raw_value / inverse_precision
