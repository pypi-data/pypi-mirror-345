# General (Node)
#: :obj:`int`
from typing import Final

MAX_N2K_MODEL_ID_LEN: Final = 32
#: :obj:`Final`
MAX_N2K_SW_CODE_LEN: Final = 32
#: :obj:`int`
MAX_N2K_MODEL_VERSION_LEN: Final = 32
#: :obj:`int`
MAX_N2K_MODEL_SERIAL_CODE_LEN: Final = 32
#: :obj:`int`
MAX_N2K_PRODUCT_INFO_STR_LEN: Final = 32

#: :obj:`int`
Max_N2K_CONFIGURATION_INFO_FIELD_LEN: Final = 70

MAX_CAN_FRAME_DATA_LEN: Final = 8


N2K_MESSAGE_GROUPS: Final = 2
N2K_MAX_CAN_BUS_ADDRESS: Final = 251
N2K_NULL_CAN_BUS_ADDRESS: Final = 254
N2K_BROADCAST_CAN_BUS_ADDRESS: Final = 255

N2K_ADDRESS_CLAIM_TIMEOUT: Final = 250
MAX_HEARTBEAT_INTERVAL: Final = 655320

TP_MAX_FRAMES: Final = (
    5  # Maximum amount of Frames that can be received at a single time # TODO: why?
)
TP_CM_BAM: Final = 32
TP_CM_RTS: Final = 16
TP_CM_CTS: Final = 17
TP_CM_ACK: Final = 19
TP_CM_Abort: Final = 255

TP_CM_AbortBusy: Final = 1
TP_CM_AbortNoResources: Final = 2
TP_CM_AbortTimeout: Final = 3


MAX_BINARY_STATUS_ENTRIES: Final = 28


# Messages
N2K_DOUBLE_NA: Final = -1e9
N2K_FLOAT_NA: Final = -1e9
N2K_UINT8_NA: Final = 0xFF
N2K_INT8_NA: Final = 0x7F
N2K_UINT16_NA: Final = 0xFFFF
N2K_INT16_NA: Final = 0x7FFF
N2K_UINT24_NA: Final = 0xFFFFFF
N2K_INT24_NA: Final = 0x7FFFFF
N2K_UINT32_NA: Final = 0xFFFFFFFF
N2K_INT32_NA: Final = 0x7FFFFFFF
N2K_UINT64_NA: Final = 0xFFFFFFFFFFFFFFFF
N2K_INT64_NA: Final = 0x7FFFFFFFFFFFFFFF


# Message
N2K_INT8_OR: Final = 0x7E
N2K_UINT8_OR: Final = 0xFE
N2K_INT16_OR: Final = 0x7FFE
N2K_UINT16_OR: Final = 0xFFFE
N2K_INT24_OR: Final = 0x7FFFFE
N2K_UINT24_OR: Final = 0xFFFFFE
N2K_INT32_OR: Final = 0x7FFFFFFE
N2K_UINT32_OR: Final = 0xFFFFFFFE

N2K_INT32_MIN: Final = -0x80000000
N2K_INT24_MIN: Final = -0x800000
N2K_INT16_MIN: Final = -0x8000
N2K_INT8_MIN: Final = -0x80


# Device List

N2K_MAX_BUS_DEVICES: Final = 254

N2K_DL_TIME_FOR_FIRST_REQUEST: Final = (
    1000  # Time in ms for first request after device has been noticed on the bus
)
N2K_DL_TIME_BETWEEN_PI_REQUEST: Final = (
    1000  # Time in ms between product information requests
)
N2K_DL_TIME_BETWEEN_CI_REQUEST: Final = (
    1000  # Time in ms between configuration information requests
)
N2K_DL_TIME_BETWEEN_PL_REQUEST: Final = 1000  # Time in ms between PGN list requests


# Can Message Buffer

MAX_N2K_MSG_BUF_TIME: Final = 100

STR_NULL_CHAR: Final = 0xFF
