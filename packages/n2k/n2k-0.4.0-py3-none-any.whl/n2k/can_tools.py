# convert can message to usable format somehow
# e.g. by converting id
from __future__ import annotations

from dataclasses import dataclass
from typing import Final

PDU1_FORMAT_BYTE_MAX: Final = 240


@dataclass(frozen=True, kw_only=True)
class MsgHeader:
    source: int
    priority: int
    destination: int
    pgn: int


def can_id_to_n2k(can_id: int) -> MsgHeader:
    can_id_pf = (can_id >> 16) & 0xFF
    can_id_ps = (can_id >> 8) & 0xFF
    can_id_dp = (can_id >> 24) & 1

    src = (can_id >> 0) & 0xFF
    prio = (can_id >> 26) & 0x7

    if can_id_pf < PDU1_FORMAT_BYTE_MAX:
        # PDU1 format, the PS contains the destination address
        dst = can_id_ps
        pgn = (can_id_dp << 16) | (can_id_pf << 8)
    else:
        # PDU2 format, the destination is implied global and the PGN is extended
        dst = 0xFF
        pgn = (can_id_dp << 16) | (can_id_pf << 8) | can_id_ps

    return MsgHeader(source=src, priority=prio, destination=dst, pgn=pgn)


def n2k_id_to_can(
    data: MsgHeader,
) -> int | None:
    priority = data.priority & 0xFF
    pgn = data.pgn & 0xFFFFFFFF
    source = data.source & 0xFFFFFFFF
    destination = data.destination & 0xFF

    can_id_pf = (pgn >> 8) & 0xFF

    if can_id_pf < PDU1_FORMAT_BYTE_MAX:
        # PDU1 format
        if pgn & 0xFF != 0:
            # for PDU1 format, the lowest byte of the PGN has to be 0, to leave space for the destination
            return None
        return (priority & 0x7) << 26 | pgn << 8 | destination << 8 | source
    # PDU2 format
    return (priority & 0x7) << 26 | pgn << 8 | source
