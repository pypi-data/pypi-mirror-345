from n2k import constants
from n2k.message import Message
from n2k.utils import IntRef


def test_float() -> None:
    for val in [
        constants.N2K_FLOAT_NA,
        0.0,
        1.0,
        1.1230000257492065,
        -123.32099914550781,
    ]:
        msg = Message()
        msg.add_float(val)
        index = IntRef(0)
        assert msg.get_float(index) == val


def test_1_byte_udouble() -> None:
    for val in [constants.N2K_DOUBLE_NA, 0.0, 1.502, 2.512]:
        for precision in [0.1, 0.01]:
            inverse_precision = round(1 / precision)
            ret_val = round(val / precision) / inverse_precision

            msg = Message()
            msg.add_1_byte_udouble(val, precision)
            index = IntRef(0)
            assert msg.get_1_byte_udouble(precision, index) == ret_val


def test_1_byte_double() -> None:
    for val in [constants.N2K_DOUBLE_NA, 0.0, 1.1256, -1.1256]:
        for precision in [0.1, 0.01]:
            inverse_precision = round(1 / precision)
            ret_val = round(val / precision) / inverse_precision

            msg = Message()
            msg.add_1_byte_double(val, precision)
            index = IntRef(0)
            assert msg.get_1_byte_double(precision, index) == ret_val


def test_2_byte_udouble() -> None:
    for val in [constants.N2K_DOUBLE_NA, 0.0, 1.502, 2.512, 5.123, 20.69584, 652.654]:
        for precision in [0.1, 0.01]:
            inverse_precision = round(1 / precision)
            ret_val = round(val / precision) / inverse_precision

            msg = Message()
            msg.add_2_byte_udouble(val, precision)
            index = IntRef(0)
            assert msg.get_2_byte_udouble(precision, index) == ret_val


def test_2_byte_double() -> None:
    for val in [constants.N2K_DOUBLE_NA, 0.0, 1.1256, -1.1256, 2.512, -237.136]:
        for precision in [0.1, 0.01]:
            inverse_precision = round(1 / precision)
            ret_val = round(val / precision) / inverse_precision

            msg = Message()
            msg.add_2_byte_double(val, precision)
            index = IntRef(0)
            assert msg.get_2_byte_double(precision, index) == ret_val


def test_3_byte_udouble() -> None:
    for val in [constants.N2K_DOUBLE_NA, 0.0, 1.502, 2.512, 5.123, 20.69584, 16252.654]:
        for precision in [0.1, 0.01, 1e-3]:
            inverse_precision = round(1 / precision)
            ret_val = round(val / precision) / inverse_precision

            msg = Message()
            msg.add_3_byte_udouble(val, precision)
            index = IntRef(0)
            assert msg.get_3_byte_udouble(precision, index) == ret_val


def test_3_byte_double() -> None:
    for val in [constants.N2K_DOUBLE_NA, 0.0, 1.1256, -1.1256, 2.512, -4237.136]:
        for precision in [0.1, 0.01, 1e-3]:
            inverse_precision = round(1 / precision)
            ret_val = round(val / precision) / inverse_precision

            msg = Message()
            msg.add_3_byte_double(val, precision)
            index = IntRef(0)
            assert msg.get_3_byte_double(precision, index) == ret_val


def test_4_byte_udouble() -> None:
    for val in [constants.N2K_DOUBLE_NA, 0.0, 1.502, 2.512, 5.123, 20.69584, 16252.654]:
        for precision in [0.1, 0.01, 1e-3, 1e-4, 1e-5]:
            inverse_precision = round(1 / precision)
            ret_val = round(val / precision) / inverse_precision

            msg = Message()
            msg.add_4_byte_udouble(val, precision)
            index = IntRef(0)
            assert msg.get_4_byte_udouble(precision, index) == ret_val


def test_4_byte_double() -> None:
    for val in [constants.N2K_DOUBLE_NA, 0.0, 1.1256, -1.1256, 2.512, -4237.136]:
        for precision in [0.1, 0.01, 1e-3, 1e-4, 1e-5]:
            inverse_precision = round(1 / precision)
            ret_val = round(val / precision) / inverse_precision

            msg = Message()
            msg.add_4_byte_double(val, precision)
            index = IntRef(0)
            assert msg.get_4_byte_double(precision, index) == ret_val


def test_8_byte_double() -> None:
    for val in [
        constants.N2K_DOUBLE_NA,
        0.0,
        1.1256,
        -1.1256,
        2.512,
        -4237.136,
        12456.3245123,
    ]:
        for precision in [0.1, 0.01, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7]:
            inverse_precision = round(1 / precision)
            ret_val = round(val / precision) / inverse_precision

            msg = Message()
            msg.add_8_byte_double(val, precision)
            index = IntRef(0)
            assert msg.get_8_byte_double(precision, index) == ret_val


def test_byte_uint() -> None:
    for val in [constants.N2K_UINT8_NA, 0, 255]:
        msg = Message()
        msg.add_byte_uint(val)
        index = IntRef(0)
        assert msg.get_byte_uint(index) == val


def test_byte_int() -> None:
    for val in [constants.N2K_INT8_NA, 0, -0x80, 0x7F]:
        msg = Message()
        msg.add_byte_int(val)
        index = IntRef(0)
        assert msg.get_byte_int(index) == val


def test_2_byte_uint() -> None:
    for val in [constants.N2K_UINT16_NA, 0, 0xFF, 0xFFFF]:
        msg = Message()
        msg.add_2_byte_uint(val)
        index = IntRef(0)
        assert msg.get_2_byte_uint(index) == val


def test_2_byte_int() -> None:
    for val in [constants.N2K_INT16_NA, 0, -0x80, 0x7F, -0x8000, 0x7FFF]:
        msg = Message()
        msg.add_2_byte_int(val)
        index = IntRef(0)
        assert msg.get_2_byte_int(index) == val


def test_3_byte_uint() -> None:
    for val in [constants.N2K_UINT24_NA, 0, 0xFF, 0xFFFF, 0xFFFFFF]:
        msg = Message()
        msg.add_3_byte_uint(val)
        index = IntRef(0)
        assert msg.get_3_byte_uint(index) == val


def test_3_byte_int() -> None:
    for val in [
        constants.N2K_INT24_NA,
        0,
        -0x80,
        0x7F,
        -0x8000,
        0x7FFF,
        -0x800000,
        0x7FFFFF,
    ]:
        msg = Message()
        msg.add_3_byte_int(val)
        index = IntRef(0)
        assert msg.get_3_byte_int(index) == val


def test_4_byte_uint() -> None:
    for val in [constants.N2K_UINT32_NA, 0, 0xFF, 0xFFFF, 0xFFFFFF, 0xFFFFFFFF]:
        msg = Message()
        msg.add_4_byte_uint(val)
        index = IntRef(0)
        assert msg.get_4_byte_uint(index) == val


def test_8_byte_uint() -> None:
    for val in [
        constants.N2K_UINT64_NA,
        0,
        0xFF,
        0xFFFF,
        0xFFFFFF,
        0xFFFFFFFF,
        0xFFFFFFFFFFFFFFFF,
    ]:
        msg = Message()
        msg.add_uint_64(val)
        index = IntRef(0)
        assert msg.get_uint_64(index) == val


def test_str() -> None:
    val = "Test 123456"
    msg = Message()
    msg.add_str(val, len(val))
    index = IntRef(0)
    assert msg.get_str(len(val), index) == val


def test_str_filling() -> None:
    val = "Test 123456"
    msg = Message()
    msg.add_str(val, len(val) + 4)
    index = IntRef(0)
    assert msg.get_str(len(val) + 4, index) == val


def test_var_str() -> None:
    val = "Test 123456"
    msg = Message()
    msg.add_var_str(val)
    index = IntRef(0)
    assert msg.get_var_str(index) == val


def test_ais_str() -> None:
    val = "Test 123456"
    msg = Message()
    msg.add_ais_str(val, len(val))
    index = IntRef(0)
    assert msg.get_str(len(val), index) == val.upper()


def test_ais_str_filling() -> None:
    val = "Test 123456"
    msg = Message()
    msg.add_ais_str(val, len(val) + 6)
    index = IntRef(0)
    assert msg.get_str(len(val) + 6, index) == val.upper()
