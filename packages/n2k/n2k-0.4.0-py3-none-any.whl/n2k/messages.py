from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, Literal

from n2k import constants, types
from n2k.message import Message
from n2k.n2k import PGN
from n2k.utils import IntRef, with_fallback

if TYPE_CHECKING:
    from n2k.device_information import DeviceInformation


# System Date/Time (PGN 126992)
@dataclass(frozen=True, kw_only=True)
class SystemTime:
    """
    Data for System Date/Time Message (PGN 126992)

    System Time is in UTC.
    """

    #: Days since 1970-01-01
    system_date: int
    # TODO: check if seconds since midnight is UTC or timezone specific
    #: Seconds since midnight
    system_time: float
    #: Time source, see :py:class:`n2k.types.N2kTimeSource`
    time_source: types.N2kTimeSource
    #: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
    #: for different messages to indicate that they are measured at same time.
    sid: int = constants.N2K_UINT8_NA


def create_n2k_system_time_message(
    data: SystemTime,
) -> Message:
    """
    Generate NMEA2000 message containing specified System Date/Time (PGN 126992).

    :param data: See :py:class:`SystemTime`
    :return: NMEA2000 message ready to be sent.
    """
    msg = Message()
    msg.pgn = PGN.SystemDateTime
    msg.priority = 3
    msg.add_byte_uint(data.sid)
    msg.add_byte_uint((data.time_source & 0x0F) | 0xF0)
    msg.add_2_byte_uint(data.system_date)
    msg.add_4_byte_double(data.system_time, 1e-4)
    return msg


def parse_n2k_system_time(msg: Message) -> SystemTime:
    """
    Parse System Time information from a PGN 126992 message.

    :param msg: NMEA2000 Message with PGN 126992
    :return: Object containing the parsed information.
    """
    index = IntRef(0)
    return SystemTime(
        sid=msg.get_byte_uint(index),
        time_source=types.N2kTimeSource(msg.get_byte_uint(index) & 0x0F),
        system_date=msg.get_2_byte_uint(index),
        system_time=msg.get_4_byte_udouble(0.0001, index),
    )


# AIS Safety Related Broadcast Message (PGN 129802)
@dataclass(frozen=True, kw_only=True)
class AISSafetyRelatedBroadcast:
    """Data for AIS Safety Related Broadcast Message (PGN 129802)"""

    #: Message Type. Identifier for AIS Safety Related Broadcast Message aka Message 14; always 14.
    message_id: Literal[types.N2kAISMessageID.Safety_related_broadcast_message]
    #: Repeat indicator. Used by the repeater to indicate how many times a message has been repeated.
    #:
    #: 0-3; 0 = default; 3 = do not repeat anymore
    repeat: types.N2kAISRepeat
    #: MMSI number of source station of message
    source_id: int
    #: see :py:class:`n2k.types.N2kAISTransceiverInformation`
    ais_transceiver_information: types.N2kAISTransceiverInformation
    #: Maximum 121 bytes. Encoded as 6-bit ASCII (see ITU-R M.1371-1)
    safety_related_text: str | None


def create_n2k_ais_related_broadcast_msg_message(
    data: AISSafetyRelatedBroadcast,
) -> Message:
    """
    Generate NMEA2000 message containing AIS Safety Related Broadcast Message. (PGN 129802)

    :param data: See :py:class:`AISSafetyRelatedBroadcast`
    :return: NMEA2000 message ready to be sent.
    """
    msg = Message()
    msg.pgn = PGN.AISSafetyRelatedBroadcastMessage
    msg.priority = 5
    msg.add_byte_uint((data.repeat & 0x03) << 6 | (data.message_id & 0x3F))
    msg.add_4_byte_uint(0xC0000000 | (data.source_id & 0x3FFFFFFF))
    msg.add_byte_uint(0xE0 | (0x1F & data.ais_transceiver_information))
    msg.add_var_str(data.safety_related_text or "")
    return msg


def parse_n2k_ais_related_broadcast_msg(msg: Message) -> AISSafetyRelatedBroadcast:
    """
    Parse AIS Safety Related Broadcast Message from a PGN 129802 message

    :param msg: NMEA2000 Message with PGN 129802
    :return: Object containing the parsed information.
    """
    index = IntRef(0)
    vb = msg.get_byte_uint(index)
    message_id = types.N2kAISMessageID(vb & 0x3F)
    if message_id != types.N2kAISMessageID.Safety_related_broadcast_message:
        raise ValueError

    return AISSafetyRelatedBroadcast(
        message_id=message_id,
        repeat=types.N2kAISRepeat((vb >> 6) & 0x03),
        source_id=msg.get_4_byte_uint(index) & 0x3FFFFFFF,
        ais_transceiver_information=types.N2kAISTransceiverInformation(
            msg.get_byte_uint(index) & 0x1F,
        ),
        safety_related_text=msg.get_var_str(index),
    )


# Man Overboard Notification (PGN 127233)
@dataclass(frozen=True, kw_only=True)
class MOBNotification:
    """Data for Man Overboard Notification Message (PGN 127233)"""

    #: Identifier for each MOB emitter, unique to the vessel
    mob_emitter_id: int
    #: MOB Status, see :py:class:`n2k.types.N2kMOBStatus`
    mob_status: types.N2kMOBStatus
    #: Time of day (UTC) in seconds when MOB was initially activated
    activation_time: float
    #: Position Source, see :py:class:`n2k.types.N2kMOBPositionSource`
    position_source: types.N2kMOBPositionSource
    #: Date of MOB position in days since 1970-01-01 (UTC)
    position_date: int
    #: Time of day of MOB position (UTC) in seconds
    position_time: float
    #: Latitude in degrees
    latitude: float
    #: Longitude in degrees
    longitude: float
    #: True or Magnetic
    cog_reference: types.N2kHeadingReference
    #: Course Over Ground in radians with a resolution of 1x10E-4 rad
    cog: float
    #: Speed Over Ground in m/s with a resolution of 1x10E-2 m/s
    sog: float
    #: MMSI of vessel of Origin. Can be set to `n2k.constants.N2K_INT32_NA` if unknown
    mmsi: int
    #: see :py:class:`n2k.types.N2kMOBEmitterBatteryStatus`
    mob_emitter_battery_status: types.N2kMOBEmitterBatteryStatus
    #: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
    #: for different messages to indicate that they are measured at same time.
    sid: int = 0xFF


def create_n2k_mob_notification_message(data: MOBNotification) -> Message:
    """
    Generate NMEA2000 message containing Man Overboard Notification (PGN 127233)

    :param data: See :py:class:`MOBNotification`
    :return: NMEA2000 message ready to be sent.
    """
    msg = Message()
    msg.pgn = PGN.ManOverBoard
    msg.priority = 3
    msg.add_byte_uint(data.sid)
    msg.add_4_byte_uint(data.mob_emitter_id)
    msg.add_byte_uint((data.mob_status & 0x07) | 0xF8)
    msg.add_4_byte_udouble(data.activation_time, 0.0001)
    msg.add_byte_uint((data.position_source & 0x07) | 0xF8)
    msg.add_2_byte_uint(data.position_date)
    msg.add_4_byte_udouble(data.position_time, 0.0001)
    msg.add_4_byte_double(data.latitude, 1e-7)
    msg.add_4_byte_double(data.longitude, 1e-7)
    msg.add_byte_uint((data.cog_reference & 0x03) | 0xFC)
    msg.add_2_byte_udouble(data.cog, 0.0001)
    msg.add_2_byte_udouble(data.sog, 0.01)
    msg.add_4_byte_uint(data.mmsi)
    msg.add_byte_uint((data.mob_emitter_battery_status & 0x07) | 0xF8)
    return msg


def parse_n2k_mob_notification(msg: Message) -> MOBNotification:
    """
    Parse Man Over Board Notification from a PGN 127233 message

    :param msg: NMEA2000 Message with PGN 127233
    :return: Object containing the parsed information.
    """
    index = IntRef(0)

    return MOBNotification(
        sid=msg.get_byte_uint(index),
        mob_emitter_id=msg.get_4_byte_uint(index),
        mob_status=types.N2kMOBStatus(msg.get_byte_uint(index) & 0x07),
        activation_time=msg.get_4_byte_udouble(0.0001, index),
        position_source=types.N2kMOBPositionSource(msg.get_byte_uint(index) & 0x07),
        position_date=msg.get_2_byte_uint(index),
        position_time=msg.get_4_byte_udouble(0.0001, index),
        latitude=msg.get_4_byte_double(1e-7, index),
        longitude=msg.get_4_byte_double(1e-7, index),
        cog_reference=types.N2kHeadingReference(msg.get_byte_uint(index) & 0x03),
        cog=msg.get_2_byte_udouble(0.0001, index),
        sog=msg.get_2_byte_udouble(0.01, index),
        mmsi=msg.get_4_byte_uint(index),
        mob_emitter_battery_status=types.N2kMOBEmitterBatteryStatus(
            msg.get_byte_uint(index) & 0x07,
        ),
    )


# Heading/Track Control (PGN 127237)
@dataclass(frozen=True, kw_only=True)
class HeadingTrackControl:
    """Data for Heading/Track Control Message (PGN 127237)"""

    #: Yes/No
    rudder_limit_exceeded: types.N2kOnOff
    #: Yes/No
    off_heading_limit_exceeded: types.N2kOnOff
    #: Yes/No
    off_track_limit_exceeded: types.N2kOnOff
    #: Yes/No
    override: types.N2kOnOff
    #: Steering Mode
    steering_mode: types.N2kSteeringMode
    #: Turn Mode
    turn_mode: types.N2kTurnMode
    #: True or Magnetic
    heading_reference: types.N2kHeadingReference
    #: Port or Starboard
    commanded_rudder_direction: types.N2kRudderDirectionOrder
    #: In radians
    commanded_rudder_angle: float
    #: In radians
    heading_to_steer_course: float
    #: In radians
    track: float
    #: In radians
    rudder_limit: float
    #: In radians
    off_heading_limit: float
    #: In meters
    radius_of_turn_order: float
    #: In radians/s
    rate_of_turn_order: float
    #: In meters
    off_track_limit: float
    #: In radians
    vessel_heading: float


def create_n2k_heading_track_control_message(
    data: HeadingTrackControl,
) -> Message:
    """
    Generate NMEA2000 message containing Heading/Track Control information (PGN 127237)

    :param data: See :py:class:`HeadingTrackControl`
    :return: NMEA2000 message ready to be sent.
    """
    msg = Message()
    msg.pgn = PGN.HeadingTrackControl
    msg.priority = 2
    msg.add_byte_uint(
        (data.rudder_limit_exceeded & 0x03) << 0
        | (data.off_heading_limit_exceeded & 0x03) << 2
        | (data.off_track_limit_exceeded & 0x03) << 4
        | (data.override & 0x03) << 6,
    )
    msg.add_byte_uint(
        (data.steering_mode & 0x07) << 0
        | (data.turn_mode & 0x07) << 3
        | (data.heading_reference & 0x03) << 6,
    )
    msg.add_byte_uint((data.commanded_rudder_direction & 0x07) << 5 | 0x1F)
    msg.add_2_byte_double(data.commanded_rudder_angle, 0.0001)
    msg.add_2_byte_udouble(data.heading_to_steer_course, 0.0001)
    msg.add_2_byte_udouble(data.track, 0.0001)
    msg.add_2_byte_udouble(data.rudder_limit, 0.0001)
    msg.add_2_byte_udouble(data.off_heading_limit, 0.0001)
    msg.add_2_byte_double(data.radius_of_turn_order, 1)
    msg.add_2_byte_double(data.rate_of_turn_order, 3.125e-5)
    msg.add_2_byte_double(data.off_track_limit, 1)
    msg.add_2_byte_udouble(data.vessel_heading, 0.0001)
    return msg


def parse_n2k_heading_track_control(msg: Message) -> HeadingTrackControl:
    """
    Parse heading/track control information from a PGN 127237 message

    :param msg: NMEA2000 Message with PGN 127237
    :return: Object containing the parsed information.
    """
    index = IntRef(0)
    vb = msg.get_byte_uint(index)
    rudder_limit_exceeded = types.N2kOnOff(vb & 0x03)
    off_heading_limit_exceeded = types.N2kOnOff((vb >> 2) & 0x03)
    off_track_limit_exceeded = types.N2kOnOff((vb >> 4) & 0x03)
    override = types.N2kOnOff((vb >> 6) & 0x03)
    vb = msg.get_byte_uint(index)
    steering_mode = types.N2kSteeringMode(vb & 0x07)
    turn_mode = types.N2kTurnMode((vb >> 3) & 0x07)
    heading_reference = types.N2kHeadingReference((vb >> 6) & 0x03)
    return HeadingTrackControl(
        rudder_limit_exceeded=rudder_limit_exceeded,
        off_heading_limit_exceeded=off_heading_limit_exceeded,
        off_track_limit_exceeded=off_track_limit_exceeded,
        override=override,
        steering_mode=steering_mode,
        turn_mode=turn_mode,
        heading_reference=heading_reference,
        commanded_rudder_direction=types.N2kRudderDirectionOrder(
            (msg.get_byte_uint(index) >> 5) & 0x07,
        ),
        commanded_rudder_angle=msg.get_2_byte_double(0.0001, index),
        heading_to_steer_course=msg.get_2_byte_udouble(0.0001, index),
        track=msg.get_2_byte_udouble(0.0001, index),
        rudder_limit=msg.get_2_byte_udouble(0.0001, index),
        off_heading_limit=msg.get_2_byte_udouble(0.0001, index),
        radius_of_turn_order=msg.get_2_byte_double(1, index),
        rate_of_turn_order=msg.get_2_byte_double(3.125e-5, index),
        off_track_limit=msg.get_2_byte_double(1, index),
        vessel_heading=msg.get_2_byte_udouble(0.0001, index),
    )


# Rudder (PGN 127245)
@dataclass(frozen=True, kw_only=True)
class Rudder:
    """Data for Rudder Message (PGN 127245)"""

    #: Current rudder position in radians.
    rudder_position: float
    #: Rudder instance.
    instance: int
    #: Direction, where rudder should be turned.
    rudder_direction_order: types.N2kRudderDirectionOrder
    #: Angle where rudder should be turned in radians.
    angle_order: float


def create_n2k_rudder_message(
    data: Rudder,
) -> Message:
    """
    Generate NMEA2000 message containing Rudder information (PGN 127245)

    :param data: See :py:class:`Rudder`
    :return: NMEA2000 Message ready to be sent.
    """
    msg = Message()
    msg.pgn = PGN.Rudder
    msg.priority = 2
    msg.add_byte_uint(data.instance)
    msg.add_byte_uint((data.rudder_direction_order & 0x07) | 0xF8)
    msg.add_2_byte_double(data.angle_order, 0.0001)
    msg.add_2_byte_double(data.rudder_position, 0.0001)
    msg.add_byte_uint(0xFF)  # reserved
    msg.add_byte_uint(0xFF)  # reserved
    return msg


def parse_n2k_rudder(msg: Message) -> Rudder:
    """
    Parse rudder control information from a PGN 127245 message

    :param msg: NMEA2000 Message with PGN 127245
    :return: Object containing the parsed information
    """
    index = IntRef(0)
    return Rudder(
        instance=msg.get_byte_uint(index),
        rudder_direction_order=types.N2kRudderDirectionOrder(
            msg.get_byte_uint(index) & 0x07,
        ),
        angle_order=msg.get_2_byte_double(0.0001, index),
        rudder_position=msg.get_2_byte_double(0.0001, index),
    )


# Vessel Heading (PGN 127250)
@dataclass(frozen=True, kw_only=True)
class Heading:
    """Data for Vessel Heading Message (PGN 127250)"""

    #: Heading in radians
    heading: float
    #: Magnetic deviation in radians. Use `N2K_DOUBLE_NA` for undefined value.
    deviation: float
    #: Magnetic variation in radians. Use `N2K_DOUBLE_NA` for undefined value.
    variation: float
    #: Heading reference. Can be true or magnetic.
    ref: types.N2kHeadingReference
    #: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
    #: for different messages to indicate that they are measured at same time.
    sid: int = 0xFF


def create_n2k_heading_message(
    data: Heading,
) -> Message:
    """
    Vessel Heading (PGN 127250).

    If the true heading is used, leave the deviation and variation undefined. Else, if the magnetic heading is sent,
    specify the magnetic deviation and variation.

    :param data: See :py:class:`Heading`
    :return: NMEA2000 message ready to be sent.
    """
    msg = Message()
    msg.pgn = PGN.VesselHeading
    msg.priority = 2
    msg.add_byte_uint(data.sid)
    msg.add_2_byte_udouble(data.heading, 0.0001)
    msg.add_2_byte_double(data.deviation, 0.0001)
    msg.add_2_byte_double(data.variation, 0.0001)
    msg.add_byte_uint(0xFC | data.ref)
    return msg


def parse_n2k_heading(msg: Message) -> Heading:
    """
    Parse heading information from a PGN 127250 message

    :param msg: NMEA2000 Message with PGN 127250
    :return: Object containing the parsed information
    """
    index = IntRef(0)

    return Heading(
        sid=msg.get_byte_uint(index),
        heading=msg.get_2_byte_udouble(0.0001, index),
        deviation=msg.get_2_byte_double(0.0001, index),
        variation=msg.get_2_byte_double(0.0001, index),
        ref=types.N2kHeadingReference(msg.get_byte_uint(index) & 0x03),
    )


# Rate of Turn (PGN 127251)
@dataclass(frozen=True, kw_only=True)
class RateOfTurn:
    """Data for Rate of Turn Message (PGN 127251)"""

    #: Rate of turn in radians per second
    rate_of_turn: float
    #: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
    #: for different messages to indicate that they are measured at same time.
    sid: int = 0xFF


def create_n2k_rate_of_turn_message(data: RateOfTurn) -> Message:
    """
    Rate of Turn (PGN 127251)

    :param data: See :py:class:`RateOfTurn`
    :return:
    """
    msg = Message()
    msg.pgn = PGN.RateOfTurn
    msg.priority = 2
    msg.add_byte_uint(data.sid)
    msg.add_4_byte_double(data.rate_of_turn, 3.125e-08)  # 1e-6/32.0
    msg.add_byte_uint(0xFF)
    msg.add_2_byte_uint(0xFFFF)
    return msg


def parse_n2k_rate_of_turn(msg: Message) -> RateOfTurn:
    """
    Parse rate of turn information from a PGN 127251 message

    :param msg: NMEA2000 Message with PGN 127251
    :return: Object containing the parsed information
    """
    index = IntRef(0)
    return RateOfTurn(
        sid=msg.get_byte_uint(index),
        rate_of_turn=msg.get_4_byte_double(3.125e-08, index),  # 1e-6/32.0
    )


# Heave (PGN 127252)
@dataclass(frozen=True, kw_only=True)
class Heave:
    """Data for Heave Message (PGN 127252)"""

    #: Vertical displacement perpendicular to the earth's surface in meters
    heave: float
    #: Delay added by calculations in seconds
    delay: float
    #: Delay Source, see type
    delay_source: types.N2kDelaySource
    #: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
    #: for different messages to indicate that they are measured at same time.
    sid: int = 0xFF


def create_n2k_heave_message(
    data: Heave,
) -> Message:
    """
    Heave (PGN 127252)

    :param data: See :py:class:`Heave`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.Heave
    msg.priority = 3
    msg.add_byte_uint(data.sid)
    msg.add_2_byte_double(data.heave, 0.01)
    msg.add_2_byte_udouble(data.delay, 0.01)
    msg.add_byte_uint(0xF0 | (data.delay_source & 0x0F))
    msg.add_2_byte_uint(constants.N2K_UINT16_NA)

    return msg


def parse_n2k_heave(msg: Message) -> Heave:
    """
    Parse heave information from a PGN 127252 message

    :param msg: NMEA2000 Message with PGN 127252
    :return: Object containing the parsed information
    """
    index = IntRef(0)
    return Heave(
        sid=msg.get_byte_uint(index),
        heave=msg.get_2_byte_double(0.01, index),
        delay=msg.get_2_byte_udouble(0.01, index),
        delay_source=types.N2kDelaySource(msg.get_byte_uint(index) & 0x0F),
    )


# Attitude (PGN 127257)
@dataclass(frozen=True, kw_only=True)
class Attitude:
    """Data for Attitude Message (PGN 127257)"""

    #: Heading in radians
    yaw: float
    #: Pitch in radians. Positive, when your bow rises.
    pitch: float
    #: Roll in radians. Positive, when tilted right.
    roll: float
    #: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
    #: for different messages to indicate that they are measured at same time.
    sid: int = 0xFF


def create_n2k_attitude_message(data: Attitude) -> Message:
    """
    Attitude (PGN 127257)

    :param data: See :py:class:`Attitude`
    :return: NMEA2000 message ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.Attitude
    msg.priority = 3
    msg.add_byte_uint(data.sid)
    msg.add_2_byte_double(data.yaw, 0.0001)
    msg.add_2_byte_double(data.pitch, 0.0001)
    msg.add_2_byte_double(data.roll, 0.0001)
    msg.add_byte_uint(0xFF)  # Reserved
    return msg


def parse_n2k_attitude(msg: Message) -> Attitude:
    """
    Parse attitude information from a PGN 127257 message

    :param msg: NMEA2000 Message with PGN 127257
    :return: Object containing the parsed information
    """
    index = IntRef(0)
    return Attitude(
        sid=msg.get_byte_uint(index),
        yaw=msg.get_2_byte_double(0.0001, index),
        pitch=msg.get_2_byte_double(0.0001, index),
        roll=msg.get_2_byte_double(0.0001, index),
    )


# Magnetic Variation (PGN 127258)
@dataclass(frozen=True, kw_only=True)
class MagneticVariation:
    """Data for Magnetic Variation Message (PGN 127258)"""

    #: How the magnetic variation for the current location has been derived
    source: types.N2kMagneticVariation
    #: UTC Date in Days since 1970
    days_since_1970: int
    #: Variation in radians, positive values represent Easterly, negative values a Westerly variation.
    variation: float
    #: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
    #: for different messages to indicate that they are measured at same time.
    sid: int = 0xFF


def create_n2k_magnetic_variation_message(data: MagneticVariation) -> Message:
    """
    Magnetic Variation (PGN 127258)

    :param data: See :py:class:`MagneticVariation`
    :return: NMEA2000 message ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.MagneticVariation
    msg.priority = 6
    msg.add_byte_uint(data.sid)
    msg.add_byte_uint(data.source & 0x0F)
    msg.add_2_byte_uint(data.days_since_1970)
    msg.add_2_byte_double(data.variation, 0.0001)
    msg.add_2_byte_uint(0xFFFF)
    return msg


def parse_n2k_magnetic_variation(msg: Message) -> MagneticVariation:
    """
    Parse magnetic variation information from a PGN 127258 message

    :param msg: NMEA2000 Message with PGN 127258
    :return: Object containing the parsed information
    """
    index = IntRef(0)
    return MagneticVariation(
        sid=msg.get_byte_uint(index),
        source=types.N2kMagneticVariation(msg.get_byte_uint(index) & 0x0F),
        days_since_1970=msg.get_2_byte_uint(index),
        variation=msg.get_2_byte_double(0.0001, index),
    )


# Engine Parameters Rapid (PGN 127488)
@dataclass(frozen=True, kw_only=True)
class EngineParametersRapid:
    """Data for Engine Parameters Rapid Message (PGN 127488)"""

    #: This field indicates the particular engine for which this data applies.
    #: A single engine will have an instance of 0.
    #: Engines in multi-engine boats will be numbered starting at 0 at the bow
    #: of the boat, incrementing to n going towards the stern of the boat.
    #: For engines at the same distance from the bow and the stern, the engines are
    #: numbered starting from the port side and proceeding towards the starboard side.
    engine_instance: int
    #: Rotational speed in RPM, stored at a precision of ¼ RPM
    engine_speed: float
    #: Turbocharger boost pressure in Pascal, stored at a precision of 100 Pa
    engine_boost_pressure: float
    #: Engine tilt or trim (positive or negative) in percent, stored as an integer.
    #:
    #: 0: full tilt down
    #: 50: neutral
    #: 100: full tilt up
    engine_tilt_trim: int


def create_n2k_engine_parameters_rapid_message(data: EngineParametersRapid) -> Message:
    """
    Engine Parameters Rapid (PGN 127488)

    :param data: See :py:class:`EngineParametersRapid`
    :return: NMEA2000 message ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.EngineParametersRapid
    msg.priority = 2
    msg.add_byte_uint(data.engine_instance)
    msg.add_2_byte_udouble(data.engine_speed, 0.25)
    msg.add_2_byte_udouble(data.engine_boost_pressure, 100)
    msg.add_byte_int(
        data.engine_tilt_trim,
    )
    msg.add_byte_uint(0xFF)  # reserved
    msg.add_byte_uint(0xFF)  # reserved
    return msg


def parse_n2k_engine_parameters_rapid(msg: Message) -> EngineParametersRapid:
    """
    Parse engine parameters rapid information from a PGN 127488 message

    :param msg: NMEA2000 Message with PGN 127488
    :return: Object containing the parsed information
    """
    index = IntRef(0)
    return EngineParametersRapid(
        engine_instance=msg.get_byte_uint(index),
        engine_speed=msg.get_2_byte_udouble(0.25, index),
        engine_boost_pressure=msg.get_2_byte_udouble(100, index),
        engine_tilt_trim=msg.get_byte_int(index),
    )


# Engine Parameters Dynamic (PGN 127489)
@dataclass(frozen=True, kw_only=True)
class EngineParametersDynamic:
    """Data for Engine Parameters Dynamic Message (PGN 127489)"""

    #: This field indicates the particular engine for which this data applies.
    #: A single engine will have an instance of 0.
    #: Engines in multi-engine boats will be numbered starting at 0 at the bow
    #: of the boat, incrementing to n going towards the stern of the boat.
    #: For engines at the same distance from the bow and the stern, the engines are
    #: numbered starting from the port side and proceeding towards the starboard side.
    engine_instance: int
    #: Oil pressure of the engine in Pascal, precision 100Pa
    engine_oil_press: float
    #: Oil temperature of the engine in degrees Kelvin, precision 0.1°K
    engine_oil_temp: float
    #: Engine coolant temperature in degrees Kelvin, precision 0.1°K
    engine_coolant_temp: float
    #: Alternator voltage in Volt, precision 0.01V
    alternator_voltage: float
    #: Fuel consumption rate in cubic meters per hour, precision 0.0001 m³/h
    fuel_rate: float
    #: Cumulative runtime of the engine in seconds
    engine_hours: float
    #: Engine coolant pressure in Pascal, precision 100 Pa
    engine_coolant_press: float
    #: Fuel pressure in Pascal, precision 1000 Pa
    engine_fuel_press: float
    #: Percent engine load, precision 1%
    engine_load: int
    #: Percent engine torque, precision 1%
    engine_torque: int
    #: Warning conditions part 1
    status1: types.N2kEngineDiscreteStatus1
    #: Warning conditions part 2
    status2: types.N2kEngineDiscreteStatus2


def create_n2k_engine_parameters_dynamic_message(
    data: EngineParametersDynamic,
) -> Message:
    """
    Engine Parameters Dynamic (PGN 127489)

    :param data: See :py:class:`EngineParametersDynamic`
    :return:
    """
    msg = Message()
    msg.pgn = PGN.EngineParametersDynamic
    msg.priority = 2
    msg.add_byte_uint(data.engine_instance)
    msg.add_2_byte_udouble(data.engine_oil_press, 100)
    msg.add_2_byte_udouble(data.engine_oil_temp, 0.1)
    msg.add_2_byte_udouble(data.engine_coolant_temp, 0.01)
    msg.add_2_byte_double(data.alternator_voltage, 0.01)
    msg.add_2_byte_double(data.fuel_rate, 0.1)
    msg.add_4_byte_udouble(data.engine_hours, 1)
    msg.add_2_byte_udouble(data.engine_coolant_press, 100)
    msg.add_2_byte_udouble(data.engine_fuel_press, 1000)
    msg.add_byte_uint(0xFF)  # reserved
    msg.add_2_byte_uint(data.status1.status)
    msg.add_2_byte_uint(data.status2.status)
    msg.add_byte_uint(data.engine_load)
    msg.add_byte_uint(data.engine_torque)
    return msg


def parse_n2k_engine_parameters_dynamic(msg: Message) -> EngineParametersDynamic:
    """
    Parse engine parameters dynamic information from a PGN 127489 message

    :param msg: NMEA2000 Message with PGN 127489
    :return: Object containing the parsed information
    """
    index = IntRef(0)

    engine_instance = msg.get_byte_uint(index)
    engine_oil_press = msg.get_2_byte_udouble(100, index)
    engine_oil_temp = msg.get_2_byte_udouble(0.1, index)
    engine_coolant_temp = msg.get_2_byte_udouble(0.01, index)
    alternator_voltage = msg.get_2_byte_double(0.01, index)
    fuel_rate = msg.get_2_byte_double(0.1, index)
    engine_hours = msg.get_4_byte_udouble(1, index)
    engine_coolant_press = msg.get_2_byte_udouble(100, index)
    engine_fuel_press = msg.get_2_byte_udouble(1000, index)

    msg.get_byte_uint(index)
    status1 = types.N2kEngineDiscreteStatus1.from_status(msg.get_2_byte_uint(index))
    status2 = types.N2kEngineDiscreteStatus2.from_status(msg.get_2_byte_uint(index))
    engine_load = msg.get_byte_uint(index)
    engine_torque = msg.get_byte_uint(index)

    return EngineParametersDynamic(
        engine_instance=engine_instance,
        engine_oil_press=engine_oil_press,
        engine_oil_temp=engine_oil_temp,
        engine_coolant_temp=engine_coolant_temp,
        alternator_voltage=alternator_voltage,
        fuel_rate=fuel_rate,
        engine_hours=engine_hours,
        engine_coolant_press=engine_coolant_press,
        engine_fuel_press=engine_fuel_press,
        status1=status1,
        status2=status2,
        engine_load=engine_load,
        engine_torque=engine_torque,
    )


# Transmission parameters, dynamic (PGN 127493)
@dataclass(frozen=True, kw_only=True)
class TransmissionParametersDynamic:
    """Data for Transmission Parameters Dynamic Message (PGN 127493)"""

    #: This field indicates the particular engine for which this data applies.
    #: A single engine will have an instance of 0.
    #: Engines in multi-engine boats will be numbered starting at 0 at the bow
    #: of the boat, incrementing to n going towards the stern of the boat.
    #: For engines at the same distance from the bow and the stern, the engines are
    #: numbered starting from the port side and proceeding towards the starboard side.
    engine_instance: int
    #: The current gear the transmission is in
    transmission_gear: types.N2kTransmissionGear
    #: Transmission oil pressure in Pascal, precision 100 Pa
    oil_pressure: float
    #: Transmission oil temperature in degrees Kelvin, precision 0.1°K
    oil_temperature: float
    #: Transmission warning conditions.
    discrete_status1: types.N2kTransmissionDiscreteStatus1


def create_n2k_transmission_parameters_dynamic_message(
    data: TransmissionParametersDynamic,
) -> Message:
    """
    Transmission Parameters, Dynamic (PGN 127493)

    :param data: See :py:class:`TransmissionParametersDynamic`
    :return:
    """
    msg = Message()
    msg.pgn = PGN.TransmissionParameters
    msg.priority = 2
    msg.add_byte_uint(data.engine_instance)
    msg.add_byte_uint((data.transmission_gear & 0x03) | 0xFC)
    msg.add_2_byte_udouble(data.oil_pressure, 100)
    msg.add_2_byte_udouble(data.oil_temperature, 0.1)
    msg.add_byte_uint(data.discrete_status1.status)
    msg.add_byte_uint(0xFF)  # Reserved
    return msg


def parse_n2k_transmission_parameters_dynamic(
    msg: Message,
) -> TransmissionParametersDynamic:
    """
    Parse transmission parameters dynamic information from a PGN 127493 message

    :param msg: NMEA2000 Message with PGN 127493
    :return: Object containing the parsed information
    """
    index = IntRef(0)
    return TransmissionParametersDynamic(
        engine_instance=msg.get_byte_uint(index),
        transmission_gear=types.N2kTransmissionGear(msg.get_byte_uint(index) & 0x03),
        oil_pressure=msg.get_2_byte_udouble(100, index),
        oil_temperature=msg.get_2_byte_udouble(0.1, index),
        discrete_status1=types.N2kTransmissionDiscreteStatus1.from_status(
            msg.get_byte_uint(index) & 0x1F,
        ),
    )


# Trip Parameters, Engine (PGN 127497)
@dataclass(frozen=True, kw_only=True)
class TripFuelConsumptionEngine:
    """Data for Trip Fuel Consumption by Engine Message (PGN 127497)"""

    #: This field indicates the particular engine for which this data applies.
    #: A single engine will have an instance of 0.
    #: Engines in multi-engine boats will be numbered starting at 0 at the bow
    #: of the boat, incrementing to n going towards the stern of the boat.
    #: For engines at the same distance from the bow and the stern, the engines are
    #: numbered starting from the port side and proceeding towards the starboard side.
    engine_instance: int
    #: Fuel used by this engine during the trip in Litres, precision 1L
    trip_fuel_used: float
    #: Fuel used on average by this engine in Litres per hour, precision 0.1L/h
    fuel_rate_average: float
    #: Unknown? Litres per hour, precision 0.1L/h
    fuel_rate_economy: float
    #: Fuel used at this moment by this engine in Litres per hour, precision 0.1L/h
    instantaneous_fuel_economy: float


def create_n2k_trip_parameters_engine_message(
    data: TripFuelConsumptionEngine,
) -> Message:
    """
    Trip Fuel Consumption by Engine (PGN 127497)

    :param data: See :py:class:`TripFuelConsumptionEngine`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.TripFuelConsumptionEngine
    msg.priority = 2
    msg.add_byte_uint(data.engine_instance)
    msg.add_2_byte_udouble(data.trip_fuel_used, 1)
    msg.add_2_byte_double(data.fuel_rate_average, 0.1)
    msg.add_2_byte_double(data.fuel_rate_economy, 0.1)
    msg.add_2_byte_double(data.instantaneous_fuel_economy, 0.1)
    return msg


def parse_n2k_trip_parameters_engine(msg: Message) -> TripFuelConsumptionEngine:
    """
    Parse trip fuel consumption by engine information from a PGN 127497 message

    :param msg: NMEA2000 Message with PGN 127497
    :return: Object containing the parsed information
    """
    index = IntRef(0)
    return TripFuelConsumptionEngine(
        engine_instance=msg.get_byte_uint(index),
        trip_fuel_used=msg.get_2_byte_udouble(1, index),
        fuel_rate_average=msg.get_2_byte_double(0.1, index),
        fuel_rate_economy=msg.get_2_byte_double(0.1, index),
        instantaneous_fuel_economy=msg.get_2_byte_double(0.1, index),
    )


# Binary status report (PGN 127501)
@dataclass(frozen=True, kw_only=True)
class BinaryStatusReport:
    """Data for Binary Status Report Message (PGN 127501)"""

    #: Device or Bank Instance. This is the instance number of the device that is being reported on.
    device_bank_instance: int
    #: Full bank status. Read single status by using :py:func:`n2k.utils.n2k_get_status_on_binary_status`
    bank_status: types.N2kBinaryStatus


def create_n2k_binary_status_report_message(data: BinaryStatusReport) -> Message:
    """
    Binary Status Report (PGN 127501)

    :param data: See :py:class:`BinaryStatusReport`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.BinaryStatusReport
    msg.priority = 3
    msg.add_uint_64((data.bank_status << 8) | (data.device_bank_instance & 0xFF))
    return msg


def parse_n2k_binary_status_report(msg: Message) -> BinaryStatusReport:
    """
    Parse binary status report information from a PGN 127501 message

    :param msg: NMEA2000 Message with PGN 127501
    :return: Object containing the parsed information
    """
    index = IntRef(0)
    vb = msg.get_uint_64(index)
    return BinaryStatusReport(
        device_bank_instance=vb & 0xFF,
        bank_status=vb >> 8,
    )


# Switch Bank Control (PGN 127502)
@dataclass(frozen=True, kw_only=True)
class SwitchBankControl:
    """Data for Switch Bank Control Message (PGN 127502)"""

    #: Instance number of the switch bank that was targeted by this switch bank control message.
    target_bank_instance: int
    #: The binary status component of the switch bank control containing the commanded state of channels on the target switch bank
    #:
    #: Use :py:func:`n2k.utils.n2k_get_status_on_binary_status` to get single status
    bank_status: types.N2kBinaryStatus


def create_n2k_switch_bank_control_message(
    data: SwitchBankControl,
) -> Message:
    """
    Switch Bank Control (PGN 127502)

    This PGN is deprecated by NMEA and modern switch bank devices may well not support it, favouring PGN 126208 Command Group Function.

    Command channel states on a remote switch bank. Up to 28 remote binary states can be controlled.

    When you create a tN2kBinaryStatus object for use with this function you should ensure that you only command (that is set ON or OFF) those channels which you intend to operate.
    Channels in which you have no interest should not be commanded but set not available.

    Review :py:func:`n2k.utils.n2k_reset_binary_status`, :py:func:`n2k.utils.n2k_set_status_binary_on_status` and the documentation of :py:class:`n2k.types.N2kOnOff` for information on how to set up bank status.

    Remember as well, that transmission of a PGN 127502 message is equivalent to issuing a command, so do not send the same message repeatedly: once should be enough.
    You can always check that the target switch bank has responded by checking its PGN 127501 broadcasts.

    :param data: See :py:class:`SwitchBankControl`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.SwitchBankControl
    msg.priority = 3
    msg.add_uint_64((data.bank_status << 8) | (data.target_bank_instance & 0xFF))
    return msg


def parse_n2k_switch_bank_control(msg: Message) -> SwitchBankControl:
    """
    Parse switch bank control information from a PGN 127502 message

    :param msg: NMEA2000 Message with PGN 127502
    :return: Object containing the parsed information
    """
    index = IntRef(0)
    vb = msg.get_uint_64(index)
    return SwitchBankControl(
        target_bank_instance=vb & 0xFF,
        bank_status=vb >> 8,
    )


# Fluid level (PGN 127505)
@dataclass(frozen=True, kw_only=True)
class FluidLevel:
    """Data for Fluid Level Message (PGN 127505)"""

    #: Tank instance. Different devices handles this a bit differently.
    instance: int
    #: Type of fluid.
    fluid_type: types.N2kFluidType
    #: Tank level in % of full tank, precision 0.004%
    level: float
    #: Tank capacity in litres, precision 0.1L
    capacity: float


def create_n2k_fluid_level_message(data: FluidLevel) -> Message:
    """
    Fluid Level (PGN 127505)

    :param data: See :py:class:`FluidLevel`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.priority = 6
    msg.add_byte_uint((data.instance & 0x0F) | ((data.fluid_type & 0x0F) << 4))
    msg.add_2_byte_double(data.level, 0.004)
    msg.add_4_byte_udouble(data.capacity, 0.1)
    msg.add_byte_uint(0xFF)  # Reserved
    return msg


def parse_n2k_fluid_level(msg: Message) -> FluidLevel:
    """
    Parse fluid level information from a PGN 127505 message

    :param msg: NMEA2000 Message with PGN 127505
    :return: Object containing the parsed information
    """
    index = IntRef(0)
    vb = msg.get_byte_uint(index)

    return FluidLevel(
        instance=vb & 0x0F,
        fluid_type=types.N2kFluidType((vb >> 4) & 0x0F),
        level=msg.get_2_byte_double(0.004, index),
        capacity=msg.get_4_byte_udouble(0.1, index),
    )


# DC Detailed Status (PGN 127506)
@dataclass(frozen=True, kw_only=True)
class DCDetailedStatus:
    """Data for DC Detailed Status Message (PGN 127506)"""

    #: DC Source Instance
    dc_instance: int
    #: Type of DC Source
    dc_type: types.N2kDCType
    #: Percent of charge
    state_of_charge: int
    #: Percent of health
    state_of_health: int
    #: Time remaining in seconds, precision 60s
    time_remaining: float
    #: DC output voltage ripple in Volt, precision 0.001V
    ripple_voltage: float
    #: Battery capacity in coulombs, precision 3600C (aka 1Ah)
    capacity: float
    #: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
    #: for different messages to indicate that they are measured at same time.
    sid: int = 0xFF


def create_n2k_dc_detailed_status_message(data: DCDetailedStatus) -> Message:
    """
    DC Detailed Status (PGN 127506)

    :param data: See :py:class:`DCDetailedStatus`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.DCDetailedStatus
    msg.priority = 6
    msg.add_byte_uint(data.sid)
    msg.add_byte_uint(data.dc_instance)
    msg.add_byte_uint(data.dc_type)
    msg.add_byte_uint(data.state_of_charge)
    msg.add_byte_uint(data.state_of_health)
    msg.add_2_byte_udouble(data.time_remaining, 60)
    msg.add_2_byte_udouble(data.ripple_voltage, 0.001)
    msg.add_2_byte_udouble(data.capacity, 3600)
    return msg


def parse_n2k_dc_detailed_status(msg: Message) -> DCDetailedStatus:
    """
    Parse DC Detailed Status information from a PGN 127506 message

    :param msg: NMEA2000 Message with PGN 127506
    :return: Object containing the parsed information
    """
    index = IntRef(0)
    return DCDetailedStatus(
        sid=msg.get_byte_uint(index),
        dc_instance=msg.get_byte_uint(index),
        dc_type=types.N2kDCType(msg.get_byte_uint(index)),
        state_of_charge=msg.get_byte_uint(index),
        state_of_health=msg.get_byte_uint(index),
        time_remaining=msg.get_2_byte_udouble(60, index),
        ripple_voltage=msg.get_2_byte_udouble(0.001, index),
        capacity=msg.get_2_byte_udouble(3600, index),
    )


# Charger Status (PGN 127507)
@dataclass(frozen=True, kw_only=True)
class ChargerStatus:
    """Data for Charger Status Message (PGN 127507)"""

    #: Charger Instance
    instance: int
    #: Battery Instance
    battery_instance: int
    #: Operating State
    charge_state: types.N2kChargeState
    #: Charger Mode
    charger_mode: types.N2kChargerMode
    #: Yes/No
    enabled: types.N2kOnOff
    #: Yes/No
    equalization_pending: types.N2kOnOff
    #: Time remaining in seconds, precision 1s
    equalization_time_remaining: float


def create_n2k_charger_status_message(data: ChargerStatus) -> Message:
    """
    Charger Status (PGN 127507)

    :param data: See :py:class:`ChargerStatus`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.ChargerStatus
    msg.priority = 6
    msg.add_byte_uint(data.instance)
    msg.add_byte_uint(data.battery_instance)
    msg.add_byte_uint((data.charger_mode & 0x0F) << 4 | (data.charge_state & 0x0F))
    msg.add_byte_uint(
        0x0F << 4 | (data.equalization_pending & 0x03) << 2 | (data.enabled & 0x03),
    )
    msg.add_2_byte_udouble(data.equalization_time_remaining, 60)
    return msg


def parse_n2k_charger_status(msg: Message) -> ChargerStatus:
    """
    Parse charger status information from a PGN 127507 message

    :param msg: NMEA2000 Message with PGN 127507
    :return: Object containing the parsed information
    """
    index = IntRef(0)

    instance = msg.get_byte_uint(index)
    battery_instance = msg.get_byte_uint(index)
    vb = msg.get_byte_uint(index)
    charge_state = types.N2kChargeState(vb & 0x0F)
    charger_mode = types.N2kChargerMode((vb >> 4) & 0x0F)
    vb = msg.get_byte_uint(index)
    enabled = types.N2kOnOff(vb & 0x03)
    equalization_pending = types.N2kOnOff((vb >> 2) & 0x03)
    equalization_time_remaining = msg.get_2_byte_udouble(60, index)

    return ChargerStatus(
        instance=instance,
        battery_instance=battery_instance,
        charge_state=charge_state,
        charger_mode=charger_mode,
        enabled=enabled,
        equalization_pending=equalization_pending,
        equalization_time_remaining=equalization_time_remaining,
    )


# Battery Status (PGN 127508)
@dataclass(frozen=True, kw_only=True)
class BatteryStatus:
    """Data for Battery Status Message (PGN 127508)"""

    #: Battery Instance
    battery_instance: int
    #: Battery Voltage in Volt, precision 0.01V
    battery_voltage: float
    #: Battery Current in Ampere, precision 0.1A
    battery_current: float
    #: Battery Temperature in Kelvin, precision 0.01K
    battery_temperature: float
    #: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
    #: for different messages to indicate that they are measured at same time
    sid: int = 0xFF


def create_n2k_battery_status_message(data: BatteryStatus) -> Message:
    """
    Battery Status (PGN 127508)

    :param data: See :py:class:`BatteryStatus`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.BatteryStatus
    msg.priority = 6
    msg.add_byte_uint(data.battery_instance)
    msg.add_2_byte_double(data.battery_voltage, 0.01)
    msg.add_2_byte_double(data.battery_current, 0.1)
    msg.add_2_byte_udouble(data.battery_temperature, 0.01)
    msg.add_byte_uint(data.sid)
    return msg


def parse_n2k_battery_status(msg: Message) -> BatteryStatus:
    """
    Parse battery status information from a PGN 127508 message

    :param msg: NMEA2000 Message with PGN 127508
    :return: Object containing the parsed information
    """
    index = IntRef(0)
    return BatteryStatus(
        battery_instance=msg.get_byte_uint(index),
        battery_voltage=msg.get_2_byte_double(0.01, index),
        battery_current=msg.get_2_byte_double(0.1, index),
        battery_temperature=msg.get_2_byte_udouble(0.01, index),
        sid=msg.get_byte_uint(index),
    )


# Charger Configuration Status (PGN 127510)
@dataclass(frozen=True, kw_only=True)
class ChargerConfigurationStatus:
    """Data for Charger Configuration Status Message (PGN 127510)"""

    #: Charger Instance
    charger_instance: int
    #: Battery Instance
    battery_instance: int
    #: Enable/Disable charger
    enable: types.N2kOnOff
    #: Charge current limit in % range 0-252 resolution 1%
    charge_current_limit: int
    #: Charging algorithm, see type
    charging_algorithm: types.N2kChargingAlgorithm
    #: Charger mode, see type
    charger_mode: types.N2kChargerMode
    #: Battery temperature when no sensor
    battery_temperature: types.N2kBattTempNoSensor
    #: Equalize one time enable/disable
    equalization_enabled: types.N2kOnOff
    #: Enable/Disable over charge
    over_charge_enable: types.N2kOnOff
    #: Time remaining in seconds
    equalization_time_remaining: int


def create_n2k_charger_configuration_status_message(
    data: ChargerConfigurationStatus,
) -> Message:
    """
    Charger Configuration Status (PGN 127510)

    Any device capable of charging a battery can transmit this

    :param data: See :py:class:`ChargerConfigurationStatus`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.ChargerConfigurationStatus
    msg.priority = 6
    msg.add_byte_uint(data.charger_instance)
    msg.add_byte_uint(data.battery_instance)
    msg.add_byte_uint(data.enable & 0x03)
    msg.add_byte_uint(data.charge_current_limit)  # 0 - 252%
    msg.add_byte_uint(
        (data.charger_mode & 0x0F) << 4 | (data.charging_algorithm & 0x0F),
    )
    msg.add_byte_uint(
        (data.over_charge_enable & 0x03) << 6
        | (data.equalization_enabled & 0x03) << 4
        | (data.battery_temperature & 0x0F),
    )
    msg.add_2_byte_uint(data.equalization_time_remaining)
    return msg


def parse_n2k_charger_configuration_status(msg: Message) -> ChargerConfigurationStatus:
    """
    Parse charger configuration status information from a PGN 127510 message

    :param msg: NMEA2000 Message with PGN 127510
    :return: Object containing the parsed information
    """
    index = IntRef(0)

    charger_instance = msg.get_byte_uint(index)
    battery_instance = msg.get_byte_uint(index)
    enable = types.N2kOnOff(msg.get_byte_uint(index) & 0x03)
    charge_current_limit = msg.get_byte_uint(index)
    vb = msg.get_byte_uint(index)
    charging_algorithm = types.N2kChargingAlgorithm(vb & 0x0F)
    charger_mode = types.N2kChargerMode((vb >> 4) & 0x0F)
    vb = msg.get_byte_uint(index)
    battery_temperature = types.N2kBattTempNoSensor(vb & 0x0F)
    equalization_enabled = types.N2kOnOff((vb >> 4) & 0x03)
    over_charge_enable = types.N2kOnOff((vb >> 6) & 0x03)
    equalization_time_remaining = msg.get_2_byte_uint(index)

    return ChargerConfigurationStatus(
        charger_instance=charger_instance,
        battery_instance=battery_instance,
        enable=enable,
        charge_current_limit=charge_current_limit,
        charging_algorithm=charging_algorithm,
        charger_mode=charger_mode,
        battery_temperature=battery_temperature,
        equalization_enabled=equalization_enabled,
        over_charge_enable=over_charge_enable,
        equalization_time_remaining=equalization_time_remaining,
    )


# Battery Configuration Status (PGN 127513)
@dataclass(frozen=True, kw_only=True)
class BatteryConfigurationStatus:
    """Data for Battery Configuration Status Message (PGN 127513)"""

    #: Battery Instance
    battery_instance: int
    #: Battery Type, see type
    battery_type: types.N2kBatType
    #: Whether the battery supports equalization
    supports_equal: types.N2kBatEqSupport
    #: Battery nominal voltage, see type
    battery_nominal_voltage: types.N2kBatNomVolt
    #: Battery chemistry, see type
    battery_chemistry: types.N2kBatChem
    #: Battery capacity in Coulombs (aka Ampere Seconds), stored at a precision of 1Ah
    battery_capacity: float
    #: Battery temperature coefficient in %
    battery_temperature_coefficient: int
    #: Peukert Exponent, describing the relation between discharge rate and effective capacity.
    #: Value between 1.0 and 1.504
    peukert_exponent: float
    #: Charge efficiency factor
    charge_efficiency_factor: int


def create_n2k_battery_configuration_status_message(
    data: BatteryConfigurationStatus,
) -> Message:
    """
    Battery Configuration Status (PGN 127513)

    :param data: See :py:class:`BatteryConfigurationStatus`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.BatteryConfigurationStatus
    msg.priority = 6
    msg.add_byte_uint(data.battery_instance)
    msg.add_byte_uint(
        0xC0 | ((data.supports_equal & 0x03) << 4) | (data.battery_type & 0x0F),
    )  # BatType (4 bit), SupportsEqual (2 bit), Reserved (2 bit)
    msg.add_byte_uint(
        ((data.battery_chemistry & 0x0F) << 4) | (data.battery_nominal_voltage & 0x0F),
    )
    msg.add_2_byte_double(data.battery_capacity, 3600)
    msg.add_byte_uint(data.battery_temperature_coefficient)
    # Original code was unsure if this is correct.
    # I am fairly certain it is as the exponent can't be better than 1 and shouldn't be worse than 1.5
    peukert_exponent = data.peukert_exponent - 1
    if 0 <= peukert_exponent <= 0.504:  # noqa: PLR2004
        msg.add_1_byte_udouble(peukert_exponent, 0.002, -1)
    else:
        msg.add_byte_uint(constants.N2K_UINT8_NA)
    msg.add_byte_uint(data.charge_efficiency_factor)
    return msg


def parse_n2k_battery_configuration_status(msg: Message) -> BatteryConfigurationStatus:
    """
    Parse battery configuration status information from a PGN 127513 message

    :param msg: NMEA2000 Message with PGN 127513
    :return: Object containing the parsed information
    """
    index = IntRef(0)

    battery_instance = msg.get_byte_uint(index)
    vb = msg.get_byte_uint(index)
    battery_type = types.N2kBatType(vb & 0x0F)
    supports_equal = types.N2kBatEqSupport((vb >> 4) & 0x03)
    vb = msg.get_byte_uint(index)
    battery_nominal_voltage = types.N2kBatNomVolt(vb & 0x0F)
    battery_chemistry = types.N2kBatChem((vb >> 4) & 0x0F)

    return BatteryConfigurationStatus(
        battery_instance=battery_instance,
        battery_type=battery_type,
        supports_equal=supports_equal,
        battery_nominal_voltage=battery_nominal_voltage,
        battery_chemistry=battery_chemistry,
        battery_capacity=msg.get_2_byte_double(3600, index),
        battery_temperature_coefficient=msg.get_byte_uint(index),
        peukert_exponent=msg.get_1_byte_udouble(0.002, index) + 1,
        charge_efficiency_factor=msg.get_byte_uint(index),
    )


# Converter (Inverter/Charger) Status (PGN 127750)
@dataclass(frozen=True, kw_only=True)
class ConverterStatus:
    """Data for Converter Status Message (PGN 127750)"""

    #: Connection number
    connection_number: int
    #: Operating state (see :py:class:`n2k.types.N2kConvMode`)
    operating_state: types.N2kConvMode
    #: Temperature state (see :py:class:`n2k.types.N2kTemperatureState`)
    temperature_state: types.N2kTemperatureState
    #: Overload state (see :py:class:`n2k.types.N2kOverloadState`)
    overload_state: types.N2kOverloadState
    #: Low DC voltage state (see :py:class:`n2k.types.N2kDCVoltageState`)
    low_dc_voltage_state: types.N2kDCVoltageState
    #: Ripple state (see :py:class:`n2k.types.N2kRippleState`)
    ripple_state: types.N2kRippleState
    #: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
    #: for different messages to indicate that they are measured at same time.
    sid: int = 0xFF


def create_n2k_converter_status_message(data: ConverterStatus) -> Message:
    """
    Converter (Inverter/Charger) Status (PGN 127750)

    Replaces PGN 127507

    Provides state and status information about charger/inverters

    :param data: See :py:class:`ConverterStatus`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.ConverterStatus
    msg.priority = 6
    msg.add_byte_uint(data.sid)
    msg.add_byte_uint(data.connection_number)
    msg.add_byte_uint(data.operating_state)  # note: might be N2kChargeState
    msg.add_byte_uint(
        (data.ripple_state & 0x03) << 6
        | (data.low_dc_voltage_state & 0x03) << 4
        | (data.overload_state & 0x03) << 2
        | (data.temperature_state & 0x03),
    )
    msg.add_4_byte_uint(0xFFFFFFFF)  # Reserved
    return msg


def parse_n2k_converter_status(msg: Message) -> ConverterStatus:
    """
    Parse converter status information from a PGN 127750 message

    :param msg: NMEA2000 Message with PGN 127750
    :return: Object containing the parsed information
    """
    index = IntRef(0)

    sid = msg.get_byte_uint(index)
    connection_number = msg.get_byte_uint(index)
    operating_state = types.N2kConvMode(
        msg.get_byte_uint(index),
    )  # might be N2kChargeState
    vb = msg.get_byte_uint(index)
    ripple_state = types.N2kRippleState((vb >> 6) & 0x03)
    low_dc_voltage_state = types.N2kDCVoltageState((vb >> 4) & 0x03)
    overload_state = types.N2kOverloadState((vb >> 2) & 0x03)
    temperature_state = types.N2kTemperatureState(vb & 0x03)

    return ConverterStatus(
        sid=sid,
        connection_number=connection_number,
        operating_state=operating_state,
        temperature_state=temperature_state,
        overload_state=overload_state,
        low_dc_voltage_state=low_dc_voltage_state,
        ripple_state=ripple_state,
    )


# Leeway (PGN 128000)
@dataclass(frozen=True, kw_only=True)
class Leeway:
    """Data for Leeway Message (PGN 128000)"""

    #: Positive angles indicate slippage to starboard, that is, the vessel is tracking to the right of its heading,
    #: and negative angles indicate slippage to port. Angle in radians, stored at a precision of 0.0001rad
    leeway: float
    #: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
    #: for different messages to indicate that they are measured at same time.
    sid: int = 0xFF


def create_n2k_leeway_message(data: Leeway) -> Message:
    """
    Leeway (PGN 128000)

    :param data: See :py:class:`Leeway`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.Leeway
    msg.priority = 4
    msg.add_byte_uint(data.sid)
    msg.add_2_byte_double(data.leeway, 0.0001)
    msg.add_byte_uint(0xFF)  # Reserved
    msg.add_byte_uint(0xFF)  # Reserved
    msg.add_byte_uint(0xFF)  # Reserved
    msg.add_byte_uint(0xFF)  # Reserved
    msg.add_byte_uint(0xFF)  # Reserved
    return msg


def parse_n2k_leeway(msg: Message) -> Leeway:
    """
    Parse leeway information from a PGN 128000 message

    :param msg: NMEA2000 Message with PGN 128000
    :return: Object containing the parsed information
    """
    index = IntRef(0)

    return Leeway(
        sid=msg.get_byte_uint(index),
        leeway=msg.get_2_byte_double(0.0001, index),
    )


# Boat Speed (PGN 128259)
@dataclass(frozen=True, kw_only=True)
class BoatSpeed:
    """Data for Boat Speed Message (PGN 128259)"""

    #: Speed through the water in meters per second, precision 0.01m/s
    water_referenced: float
    #: Speed over ground in meters per second, precision 0.01m/s
    ground_referenced: float
    #: Type of transducer for the water referenced speed, see type
    swrt: types.N2kSpeedWaterReferenceType
    #: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
    #: for different messages to indicate that they are measured at same time.
    sid: int = 0xFF


def create_n2k_boat_speed_message(data: BoatSpeed) -> Message:
    """
    Boat Speed (PGN 128259)

    :param data: See :py:class:`BoatSpeed`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.BoatSpeed
    msg.priority = 2
    msg.add_byte_uint(data.sid)
    msg.add_2_byte_udouble(data.water_referenced, 0.01)
    msg.add_2_byte_udouble(data.ground_referenced, 0.01)
    msg.add_byte_uint(data.swrt)
    msg.add_byte_uint(0xFF)  # Reserved
    msg.add_byte_uint(0xFF)  # Reserved
    return msg


def parse_n2k_boat_speed(msg: Message) -> BoatSpeed:
    """
    Parse boat speed information from a PGN 128259 message

    :param msg: NMEA2000 Message with PGN 128259
    :return: Object containing the parsed information
    """
    index = IntRef(0)
    return BoatSpeed(
        sid=msg.get_byte_uint(index),
        water_referenced=msg.get_2_byte_udouble(0.01, index),
        ground_referenced=msg.get_2_byte_udouble(0.01, index),
        swrt=types.N2kSpeedWaterReferenceType(msg.get_byte_uint(index)),
    )


# Water depth (PGN 128267)
@dataclass(frozen=True, kw_only=True)
class WaterDepth:
    """Data for Water Depth Message (PGN 128267)"""

    #: Water depth below transducer in meters, precision 0.01m
    depth_below_transducer: float
    #: Distance in meters between transducer and water surface (positive) or transducer and keel (negative),
    #: precision 0.001m
    offset: float
    #: Maximum depth that can be measured
    max_range: float
    #: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
    #: for different messages to indicate that they are measured at same time.
    sid: int = 0xFF


def create_n2k_water_depth_message(data: WaterDepth) -> Message:
    """
    Water Depth (PGN 128267)

    :param data: See :py:class:`WaterDepth`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.WaterDepth
    msg.priority = 3
    msg.add_byte_uint(data.sid)
    msg.add_4_byte_udouble(data.depth_below_transducer, 0.01)
    msg.add_2_byte_double(data.offset, 0.001)
    msg.add_1_byte_udouble(data.max_range, 10)
    return msg


def parse_n2k_water_depth(msg: Message) -> WaterDepth:
    """
    Parse water depth information from a PGN 128267 message

    :param msg: NMEA2000 Message with PGN 128267
    :return: Object containing the parsed information
    """
    index = IntRef(0)
    return WaterDepth(
        sid=msg.get_byte_uint(index),
        depth_below_transducer=msg.get_4_byte_udouble(0.01, index),
        offset=msg.get_2_byte_double(0.001, index),
        max_range=msg.get_1_byte_udouble(10, index),
    )


# Distance log (PGN 128275)
@dataclass(frozen=True, kw_only=True)
class DistanceLog:
    """Data for Distance Log Message (PGN 128275)"""

    #: Days since 1.1.1970 UTC
    days_since_1970: int
    # TODO: are the seconds UTC?
    #: Seconds since midnight, stored at a precision of 0.0001s
    seconds_since_midnight: float
    #: Total distance traveled through the water since the installation of the device in meters.
    log: int
    #: Total distance traveled through the water since the last trip reset in meters.
    trip_log: int


def create_n2k_distance_log_message(data: DistanceLog) -> Message:
    """
    Distance Log (PGN 128275)

    :param data: See :py:class:`DistanceLog`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.DistanceLog
    msg.priority = 6
    msg.add_2_byte_uint(data.days_since_1970)
    msg.add_4_byte_udouble(data.seconds_since_midnight, 0.0001)
    msg.add_4_byte_uint(data.log)
    msg.add_4_byte_uint(data.trip_log)
    return msg


def parse_n2k_distance_log(msg: Message) -> DistanceLog:
    """
    Parse distance log information from a PGN 128275 message

    :param msg: NMEA2000 Message with PGN 128275
    :return: Object containing the parsed information
    """
    index = IntRef(0)
    return DistanceLog(
        days_since_1970=msg.get_2_byte_uint(index),
        seconds_since_midnight=msg.get_4_byte_udouble(0.0001, index),
        log=msg.get_4_byte_uint(index),
        trip_log=msg.get_4_byte_uint(index),
    )


# Anchor Windlass Control Status (PGN 128776)
@dataclass(frozen=True, kw_only=True)
class AnchorWindlassControlStatus:
    """Data for Anchor Windlass Control Status Message (PGN 128776)"""

    #: Windlass Identifier
    windlass_identifier: int
    #: Windlass Direction, see type
    windlass_direction_control: types.N2kWindlassDirectionControl
    #: Single Speed: 0=off, 1-100=on
    #:
    #: Dual Speed: 0=0ff, 1-49=slow, 50-100=fast
    #:
    #: Proportional speed: 0=off, 1-100=speed
    speed_control: int
    #: Speed control type, Single, Dual or Proportional
    speed_control_type: types.N2kSpeedType
    #: Anchor Docking Control, Yes/No
    anchor_docking_control: types.N2kGenericStatusPair
    #: Power Enable, Yes/No
    power_enable: types.N2kGenericStatusPair
    #: Mechanical Lock, Yes/No
    mechanical_lock: types.N2kGenericStatusPair
    #: Deck and Anchor Wash, Yes/No
    deck_and_anchor_wash: types.N2kGenericStatusPair
    #: Anchor Light, Yes/No
    anchor_light: types.N2kGenericStatusPair
    #: Command Timeout. Range 0.0 to 1.275 seconds, precision 0.005s
    command_timeout: float
    #: Windlass Control Events, see type
    windlass_control_events: types.N2kWindlassControlEvents
    #: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
    #: for different messages to indicate that they are measured at same time.
    sid: int = 0xFF


def create_n2k_anchor_windlass_control_status_message(
    data: AnchorWindlassControlStatus,
) -> Message:
    """
    Anchor Windlass Control Status (PGN 128776)

    :param data: See :py:class:`AnchorWindlassControlStatus`
    :return:
    """
    msg = Message()
    msg.pgn = PGN.AnchorWindlassControlStatus
    msg.priority = 2
    msg.add_byte_uint(data.sid)
    msg.add_byte_uint(data.windlass_identifier)
    msg.add_byte_uint(
        0x03 << 6
        | (data.speed_control_type & 0x03) << 4
        | (data.anchor_docking_control & 0x03) << 2
        | (data.windlass_direction_control & 0x03),
    )
    msg.add_byte_uint(data.speed_control)
    msg.add_byte_uint(
        (data.anchor_light & 0x03) << 6
        | (data.deck_and_anchor_wash & 0x03) << 4
        | (data.mechanical_lock & 0x03) << 2
        | (data.power_enable & 0x03),
    )
    msg.add_1_byte_udouble(data.command_timeout, 0.005)
    msg.add_byte_uint(data.windlass_control_events.events)
    return msg


def parse_n2k_anchor_windlass_control_status(
    msg: Message,
) -> AnchorWindlassControlStatus:
    """
    Parse anchor windlass control status information from a PGN 128776 message

    :param msg: NMEA2000 Message with PGN 128776
    :return: Object containing the parsed information
    """
    index = IntRef(0)

    sid = msg.get_byte_uint(index)
    windlass_identifier = msg.get_byte_uint(index)
    vb = msg.get_byte_uint(index)
    windlass_direction_control = types.N2kWindlassDirectionControl(vb & 0x03)
    anchor_docking_control = types.N2kGenericStatusPair((vb >> 2) & 0x03)
    speed_control_type = types.N2kSpeedType((vb >> 4) & 0x03)
    speed_control = msg.get_byte_uint(index)
    vb = msg.get_byte_uint(index)
    power_enable = types.N2kGenericStatusPair(vb & 0x03)
    mechanical_lock = types.N2kGenericStatusPair((vb >> 2) & 0x03)
    deck_and_anchor_wash = types.N2kGenericStatusPair((vb >> 4) & 0x03)
    anchor_light = types.N2kGenericStatusPair((vb >> 6) & 0x03)
    command_timeout = msg.get_1_byte_udouble(0.005, index)
    windlass_control_events = types.N2kWindlassControlEvents.from_events(
        msg.get_byte_uint(index),
    )

    return AnchorWindlassControlStatus(
        sid=sid,
        windlass_identifier=windlass_identifier,
        windlass_direction_control=windlass_direction_control,
        speed_control=speed_control,
        speed_control_type=speed_control_type,
        anchor_docking_control=anchor_docking_control,
        power_enable=power_enable,
        mechanical_lock=mechanical_lock,
        deck_and_anchor_wash=deck_and_anchor_wash,
        anchor_light=anchor_light,
        command_timeout=command_timeout,
        windlass_control_events=windlass_control_events,
    )


# Anchor Windlass Operating Status (PGN 128777)
@dataclass(frozen=True, kw_only=True)
class AnchorWindlassOperatingStatus:
    """Data for Anchor Windlass Operating Status Message (PGN 128777)"""

    #: Identifier of the windlass instance
    windlass_identifier: int
    #: Amount of rode deployed, in metres
    rode_counter_value: float
    #: Deployment speed in metres per second
    windlass_line_speed: float
    #: Windlass Motion Status, see type
    windlass_motion_status: types.N2kWindlassMotionStates
    #: Rode Type Status, see type
    rode_type_status: types.N2kRodeTypeStates
    #: Anchor Docking Status, see type
    anchor_docking_status: types.N2kAnchorDockingStates
    #: Windlass Operating Events, see type
    windlass_operating_events: types.N2kWindlassOperatingEvents
    #: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
    #: for different messages to indicate that they are measured at same time.
    sid: int = 0xFF


def create_n2k_anchor_windlass_operating_status_message(
    data: AnchorWindlassOperatingStatus,
) -> Message:
    """
    Anchor Windlass Operating Status (PGN 128777)

    :param data: See :py:class:`AnchorWindlassOperatingStatus`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.AnchorWindlassOperatingStatus
    msg.add_byte_uint(data.sid)
    msg.add_byte_uint(data.windlass_identifier)
    msg.add_byte_uint(
        0xF0
        | ((data.rode_type_status & 0x03) << 2)
        | (data.windlass_motion_status & 0x03),
    )
    msg.add_2_byte_udouble(data.rode_counter_value, 0.1)
    msg.add_2_byte_udouble(data.windlass_line_speed, 0.01)
    msg.add_byte_uint(
        (data.windlass_operating_events.event << 2)
        | (data.anchor_docking_status & 0x03),
    )
    return msg


def parse_n2k_anchor_windlass_operating_status(
    msg: Message,
) -> AnchorWindlassOperatingStatus:
    """
    Parse anchor windlass operating status information from a PGN 128777 message

    :param msg: NMEA2000 Message with PGN 128777
    :return: Object containing the parsed information
    """
    index = IntRef(0)

    sid = msg.get_byte_uint(index)
    windlass_identifier = msg.get_byte_uint(index)
    vb = msg.get_byte_uint(index)
    windlass_motion_status = types.N2kWindlassMotionStates(vb & 0x03)
    rode_type_status = types.N2kRodeTypeStates((vb >> 2) & 0x03)
    rode_counter_value = msg.get_2_byte_udouble(0.1, index)
    windlass_line_speed = msg.get_2_byte_udouble(0.01, index)
    vb = msg.get_byte_uint(index)
    anchor_docking_status = types.N2kAnchorDockingStates(vb & 0x03)
    windlass_operating_events = types.N2kWindlassOperatingEvents.from_event(vb >> 2)
    return AnchorWindlassOperatingStatus(
        sid=sid,
        windlass_identifier=windlass_identifier,
        rode_counter_value=rode_counter_value,
        windlass_line_speed=windlass_line_speed,
        windlass_motion_status=windlass_motion_status,
        rode_type_status=rode_type_status,
        anchor_docking_status=anchor_docking_status,
        windlass_operating_events=windlass_operating_events,
    )


# Anchor Windlass Monitoring Status (PGN 128778)
@dataclass(frozen=True, kw_only=True)
class AnchorWindlassMonitoringStatus:
    """Data for Anchor Windlass Monitoring Status Message (PGN 128778)"""

    #: Identifier of the windlass instance
    windlass_identifier: int
    #: Total runtime of the motor in seconds
    total_motor_time: float
    #: Voltage in Volts, precision 0.2V
    controller_voltage: float
    #: Current in Amperes, precision 1A
    motor_current: float
    #: Windlass Monitoring Events, see type
    windlass_monitoring_events: types.N2kWindlassMonitoringEvents
    #: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
    #: for different messages to indicate that they are measured at same time.
    sid: int = 0xFF


def create_n2k_anchor_windlass_monitoring_status_message(
    data: AnchorWindlassMonitoringStatus,
) -> Message:
    """
    Anchor Windlass Monitoring Status (PGN 128778)

    :param data: See :py:class:`AnchorWindlassMonitoringStatus`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.AnchorWindlassMonitoringStatus
    msg.priority = 2
    msg.add_byte_uint(data.sid)
    msg.add_byte_uint(data.windlass_identifier)
    msg.add_byte_uint(data.windlass_monitoring_events.events)
    msg.add_1_byte_udouble(data.controller_voltage, 0.2)
    msg.add_1_byte_udouble(data.motor_current, 1.0)
    msg.add_2_byte_udouble(data.total_motor_time, 60.0)
    msg.add_byte_uint(0xFF)
    return msg


def parse_n2k_anchor_windlass_monitoring_status(
    msg: Message,
) -> AnchorWindlassMonitoringStatus:
    """
    Parse anchor windlass monitoring status information from a PGN 128778 message

    :param msg: NMEA2000 Message with PGN 128778
    :return: Object containing the parsed information
    """
    index = IntRef(0)

    return AnchorWindlassMonitoringStatus(
        sid=msg.get_byte_uint(index),
        windlass_identifier=msg.get_byte_uint(index),
        windlass_monitoring_events=types.N2kWindlassMonitoringEvents.from_events(
            msg.get_byte_uint(index),
        ),
        controller_voltage=msg.get_1_byte_udouble(0.2, index),
        motor_current=msg.get_1_byte_udouble(1.0, index),
        total_motor_time=msg.get_2_byte_udouble(60.0, index),
    )


# Lat/lon rapid (PGN 129025)
@dataclass(frozen=True, kw_only=True)
class LatLonRapid:
    """Data for Lat/Lon Rapid Message (PGN 129025)"""

    #: Latitude in degrees, precision approx 1.1cm (1e-7 deg)
    latitude: float
    #: Longitude in degrees, precision approx 1.1cm at the equator (1e-7 deg)
    longitude: float


def create_n2k_lat_long_rapid_message(data: LatLonRapid) -> Message:
    """
    Position rapid update (PGN 129025)

    :param data: See :py:class:`LatLonRapid`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.LatLonRapid
    msg.priority = 2
    msg.add_4_byte_double(data.latitude, 1e-7)
    msg.add_4_byte_double(data.longitude, 1e-7)
    return msg


def parse_n2k_lat_long_rapid(msg: Message) -> LatLonRapid:
    """
    Parse latitude and longitude from a PGN 129025 message

    :param msg: NMEA2000 Message with PGN 129025
    :return: Object containing the parsed information
    """
    index = IntRef(0)

    return LatLonRapid(
        latitude=msg.get_4_byte_double(1e-7, index),
        longitude=msg.get_4_byte_double(1e-7, index),
    )


# COG SOG rapid (PGN 129026)
@dataclass(frozen=True, kw_only=True)
class CogSogRapid:
    """Data for COG/SOG Rapid Message (PGN 129026)"""

    #: Course over Ground reference, see type
    heading_reference: types.N2kHeadingReference
    #: Course over Ground in radians, precision 0.0001rad
    cog: float
    #: Speed over Ground in meters per second, precision 0.01m/s
    sog: float
    #: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
    #: for different messages to indicate that they are measured at same time.
    sid: int = 0xFF


def create_n2k_cog_sog_rapid_message(data: CogSogRapid) -> Message:
    """
    Course and Speed over Ground, rapid update (PGN 129026)

    :param data: See :py:class:`CogSogRapid`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.CogSogRapid
    msg.priority = 2
    msg.add_byte_uint(data.sid)
    msg.add_byte_uint((data.heading_reference & 0x03) | 0xFC)
    msg.add_2_byte_udouble(data.cog, 0.0001)  # Radians
    msg.add_2_byte_udouble(data.sog, 0.01)  # Meters per second
    msg.add_byte_uint(0xFF)  # Reserved
    msg.add_byte_uint(0xFF)  # Reserved
    return msg


def parse_n2k_cog_sog_rapid(msg: Message) -> CogSogRapid:
    """
    Parse course and speed over ground from a PGN 129026 message

    :param msg: NMEA2000 Message with PGN 129026
    :return: Object containing the parsed information
    """
    index = IntRef(0)

    return CogSogRapid(
        sid=msg.get_byte_uint(index),
        heading_reference=types.N2kHeadingReference(msg.get_byte_uint(index) & 0x03),
        cog=msg.get_2_byte_udouble(0.0001, index),
        sog=msg.get_2_byte_udouble(0.01, index),
    )


# GNSS Position Data (PGN 129029)
@dataclass(frozen=True, kw_only=True)
class GNSSPositionData:
    """Data for GNSS Position Data Message (PGN 129029)"""

    #: Days since 1.1.1970 UTC
    days_since_1970: int
    # TODO: check if seconds since midnight is UTC or timezone specific
    #: Seconds since midnight, stored at a precision of 0.0001s
    seconds_since_midnight: float
    #: Latitude in degrees, precision approx 11 pico metre  (a fifth of the diameter of a helium atom, 1e-16 deg).
    #: Negative values indicate south, positive indicate north.
    latitude: float
    #: Longitude in degrees, precision approx 11 pico metre at the equator (1e-16 deg)
    #: Negative values indicate west, positive indicate east.
    longitude: float
    #: Altitude in reference to the WGS-84 model in metres, precision 1 micrometer
    altitude: float
    #: GNSS Type, see type
    gnss_type: types.N2kGNSSType
    #: GNSS Method type, see type
    gnss_method: types.N2kGNSSMethod
    #: Number of satellites used for the provided data
    n_satellites: int
    #: Horizontal Dilution Of Precision in meters, precision 0.01m
    hdop: float
    #: Positional Dilution Of Precision in meters, precision 0.01m
    pdop: float
    #: Geoidal separation in meters, precision 0.01m
    geoidal_separation: float
    #: Number of Reference Stations
    n_reference_stations: int
    #: Reference Station type, see type
    reference_station_type: types.N2kGNSSType | None
    #: Reference Station ID
    reference_station_id: int | None
    #: Age of DGNSS Correction
    age_of_correction: float | None
    #: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
    #: for different messages to indicate that they are measured at same time.
    sid: int = 0xFF


def create_n2k_gnss_data_message(data: GNSSPositionData) -> Message:
    """
    GNSS Position Data (PGN 129029)

    :param data: See :py:class:`GNSSPositionData`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.GNSSPositionData
    msg.priority = 3
    msg.add_byte_uint(data.sid)
    msg.add_2_byte_uint(data.days_since_1970)
    msg.add_4_byte_udouble(data.seconds_since_midnight, 0.0001)
    msg.add_8_byte_double(data.latitude, 1e-16)
    msg.add_8_byte_double(data.longitude, 1e-16)
    msg.add_8_byte_double(data.altitude, 1e-6)
    msg.add_byte_uint((data.gnss_type & 0x0F) | (data.gnss_method & 0x0F) << 4)
    msg.add_byte_uint(1 | 0xFC)  # Integrity byte, reserved 6 bits
    msg.add_byte_uint(data.n_satellites)
    msg.add_2_byte_double(data.hdop, 0.01)
    msg.add_2_byte_double(data.pdop, 0.01)
    msg.add_4_byte_double(data.geoidal_separation, 0.01)
    if 0 < data.n_reference_stations < constants.N2K_UINT8_NA:
        msg.add_byte_uint(
            1,
        )  # Note that we have values for only one reference station, so pass only one values.
        msg.add_2_byte_int(
            (with_fallback(data.reference_station_type, types.N2kGNSSType.GPS) & 0x0F)
            | with_fallback(data.reference_station_id, constants.N2K_INT16_NA) << 4,
        )
        msg.add_2_byte_udouble(
            with_fallback(data.age_of_correction, constants.N2K_DOUBLE_NA),
            0.01,
        )
    else:
        msg.add_byte_uint(data.n_reference_stations)
    return msg


def parse_n2k_gnss_data(msg: Message) -> GNSSPositionData:
    """
    Parse GNSS Position Data information from a PGN 129029 message

    The parameters passed to ReferenceStationType, ReferenceStationID and AgeOfCorrection are set to
    :py:class:`n2k.constants.N2kGNSSType.GPS`, :py:const:`n2k.constants.N2K_INT16_NA` and :py:const:`n2k.constants.N2K_DOUBLE_NA` respectively,
    when there are no reference stations present in the message.

    :param msg: NMEA2000 Message with PGN 129029
    :return: Object containing the parsed information
    """
    index = IntRef(0)

    sid = msg.get_byte_uint(index)
    days_since_1970 = msg.get_2_byte_uint(index)
    seconds_since_midnight = msg.get_4_byte_udouble(0.0001, index)
    latitude = msg.get_8_byte_double(1e-16, index)
    longitude = msg.get_8_byte_double(1e-16, index)
    altitude = msg.get_8_byte_double(1e-6, index)
    vb = msg.get_byte_uint(index)
    gnss_type = types.N2kGNSSType(vb & 0x0F)
    gnss_method = types.N2kGNSSMethod((vb >> 4) & 0x0F)
    vb = msg.get_byte_uint(index)  # Integrity 2 bit + reserved 6 bit
    n_satellites = msg.get_byte_uint(index)
    hdop = msg.get_2_byte_double(0.01, index)
    pdop = msg.get_2_byte_double(0.01, index)
    geoidal_separation = msg.get_4_byte_double(0.01, index)
    n_reference_stations = msg.get_byte_uint(index)
    reference_station_type = None
    reference_station_id = None
    age_of_correction = None
    if 0 < n_reference_stations < constants.N2K_UINT8_NA:
        # Note that we return real number of stations, but we only have variables for one.
        vi = msg.get_2_byte_uint(index)
        reference_station_type = types.N2kGNSSType(vi & 0x0F)
        reference_station_id = vi >> 4
        age_of_correction = msg.get_2_byte_udouble(0.01, index)
    else:
        reference_station_type = types.N2kGNSSType.GPS
        reference_station_id = constants.N2K_INT16_NA
        age_of_correction = constants.N2K_DOUBLE_NA

    return GNSSPositionData(
        days_since_1970=days_since_1970,
        seconds_since_midnight=seconds_since_midnight,
        latitude=latitude,
        longitude=longitude,
        altitude=altitude,
        gnss_type=gnss_type,
        gnss_method=gnss_method,
        n_satellites=n_satellites,
        hdop=hdop,
        pdop=pdop,
        geoidal_separation=geoidal_separation,
        n_reference_stations=n_reference_stations,
        reference_station_type=reference_station_type,
        reference_station_id=reference_station_id,
        age_of_correction=age_of_correction,
        sid=sid,
    )


# Date,Time & Local offset (PGN 129033, see also PGN 126992)
@dataclass(frozen=True, kw_only=True)
class DateTimeLocalOffset:
    """
    Data for Date, Time & Local offset Message (PGN 129033)

    See also PGN 126992 (:py:class:`SystemTime`).
    """

    #: Days since 1.1.1970 UTC
    days_since_1970: int
    # TODO: UTC?
    #: Seconds since midnight, stored at a precision of 0.0001s
    seconds_since_midnight: float
    #: Local offset in minutes
    local_offset: int
    #: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
    #: for different messages to indicate that they are measured at same time
    sid: int = 0xFF


def create_n2k_date_time_local_offset_message(data: DateTimeLocalOffset) -> Message:
    """
    Date, Time & Local offset (PGN 129033), see also PGN 126992 (:py:class:`SystemTime`)

    :param data: See :py:class:`DateTimeLocalOffset`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.DateTimeLocalOffset
    msg.priority = 3
    msg.add_2_byte_uint(data.days_since_1970)
    msg.add_4_byte_udouble(data.seconds_since_midnight, 0.0001)
    msg.add_2_byte_int(data.local_offset)
    msg.add_byte_uint(data.sid)
    return msg


def parse_n2k_date_time_local_offset(msg: Message) -> DateTimeLocalOffset:
    """
    Parse date, time and local offset information from a PGN 129033 message

    :param msg: NMEA2000 Message with PGN 129033
    :return: Object containing the parsed information
    """
    index = IntRef(0)

    return DateTimeLocalOffset(
        days_since_1970=msg.get_2_byte_uint(index),
        seconds_since_midnight=msg.get_4_byte_udouble(0.0001, index),
        local_offset=msg.get_2_byte_int(index),
        sid=msg.get_byte_uint(index),
    )


# AIS position reports for Class A (PGN 129038)
@dataclass(frozen=True, kw_only=True)
class AISClassAPositionReport:
    """Data for AIS Class A Position Report Message (PGN 129038)"""

    #: Message Type ID according to https://www.itu.int/rec/R-REC-M.1371
    message_id: types.N2kAISMessageID
    #: Repeat indicator, Used by the repeater to indicate how many times a message has been repeated.
    repeat: types.N2kAISRepeat
    #: MMSI Number (Maritime Mobile Service Identity, 9 digits)
    user_id: int
    #: Latitude in degrees, precision approx 1.1cm (1e-7 deg)
    latitude: float
    #: Longitude in degrees, precision approx 1.1cm at the equator (1e-7 deg)
    longitude: float
    #: Position accuracy, 0 = low (> 10m), 1 = high (≤ 10m)
    accuracy: bool
    #: Receiver autonomous integrity monitoring (RAIM) flag of the electronic position fixing device.
    raim: bool
    #: UTC second when the report was generated by the EPFS (0-59).
    #:
    #: 60: timestamp not available, default
    #:
    #: 61: positioning system in manual input mode
    #:
    #: 62: electronic position fixing system operates in estimated (dead reckoning) mode
    #:
    #: 63: positioning system is inoperative
    seconds: int
    #: Course over Ground in radians, precision 0.0001rad
    cog: float
    #: Speed over Ground in meters per second, precision 0.01m/s
    sog: float
    #: AIS Transceiver Information, see type
    ais_transceiver_information: types.N2kAISTransceiverInformation
    #: Compass heading
    heading: float
    #: Rate of Turn
    rot: float
    #: Navigational status, see type
    nav_status: types.N2kAISNavStatus
    #: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
    #: for different messages to indicate that they are measured at same time
    sid: int = 0xFF


def create_n2k_ais_class_a_position_message(data: AISClassAPositionReport) -> Message:
    """
    AIS Position Reports for Class A (PGN 129038)

    :param data: See :py:class:`AISClassAPositionReport`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.AISClassAPositionReport
    msg.priority = 4
    msg.add_byte_uint((data.repeat & 0x03) << 6 | (data.message_id & 0x3F))
    msg.add_4_byte_uint(data.user_id)
    msg.add_4_byte_double(data.longitude, 1e-7)
    msg.add_4_byte_double(data.latitude, 1e-7)
    msg.add_byte_uint(
        (data.seconds & 0x3F) << 2 | (data.raim & 0x01) << 1 | (data.accuracy & 0x01),
    )
    msg.add_2_byte_udouble(data.cog, 1e-4)
    msg.add_2_byte_udouble(data.sog, 0.01)
    msg.add_byte_uint(0xFF)  # Communication State (19 bits)
    msg.add_byte_uint(0xFF)
    msg.add_byte_uint(((data.ais_transceiver_information & 0x1F) << 3) | 0x07)
    msg.add_2_byte_udouble(data.heading, 1e-4)
    msg.add_2_byte_double(data.rot, 3.125e-5)  # 1e-3/32.0
    msg.add_byte_uint(0xF0 | (data.nav_status & 0x0F))
    msg.add_byte_uint(0xFF)  # reserved
    msg.add_byte_uint(data.sid)
    return msg


def parse_n2k_ais_class_a_position(msg: Message) -> AISClassAPositionReport:
    """
    Parse AIS Class A Position Report information from a PGN 129038 message

    :param msg: NMEA2000 Message with PGN 129038
    :return: Object containing the parsed information
    """
    index = IntRef(0)

    vb = msg.get_byte_uint(index)
    message_id = types.N2kAISMessageID(vb & 0x3F)
    repeat = types.N2kAISRepeat((vb >> 6) & 0x03)
    user_id = msg.get_4_byte_uint(index)
    longitude = msg.get_4_byte_double(1e-7, index)
    latitude = msg.get_4_byte_double(1e-7, index)
    vb = msg.get_byte_uint(index)
    accuracy = bool(vb & 0x01)
    raim = bool((vb >> 1) & 0x01)
    seconds = (vb >> 2) & 0x3F
    cog = msg.get_2_byte_udouble(1e-4, index)
    sog = msg.get_2_byte_udouble(0.01, index)
    msg.get_byte_uint(index)  # Communication State (19 bits)
    msg.get_byte_uint(index)
    vb = msg.get_byte_uint(index)  # AIS transceiver information (5 bits)
    ais_transceiver_information = types.N2kAISTransceiverInformation((vb >> 3) & 0x1F)
    heading = msg.get_2_byte_udouble(1e-4, index)
    rot = msg.get_2_byte_double(3.125e-5, index)
    vb = msg.get_byte_uint(index)
    nav_status = types.N2kAISNavStatus(vb & 0x0F)
    msg.get_byte_uint(index)  # reserved
    sid = msg.get_byte_uint(index)

    return AISClassAPositionReport(
        message_id=message_id,
        repeat=repeat,
        user_id=user_id,
        longitude=longitude,
        latitude=latitude,
        accuracy=accuracy,
        raim=raim,
        seconds=seconds,
        cog=cog,
        sog=sog,
        ais_transceiver_information=ais_transceiver_information,
        heading=heading,
        rot=rot,
        nav_status=nav_status,
        sid=sid,
    )


# AIS position reports for Class B (PGN 129039)
@dataclass(frozen=True, kw_only=True)
class AISClassBPositionReport:
    """Data for AIS Class B Position Report Message (PGN 129039)"""

    #: Message Type ID according to https://www.itu.int/rec/R-REC-M.1371
    message_id: types.N2kAISMessageID
    #: Repeat indicator, Used by the repeater to indicate how many times a message has been repeated.
    repeat: types.N2kAISRepeat
    #: MMSI Number (Maritime Mobile Service Identity, 9 digits)
    user_id: int
    #: Latitude in degrees, precision approx 1.1cm (1e-7 deg)
    latitude: float
    #: Longitude in degrees, precision approx 1.1cm at the equator (1e-7 deg)
    longitude: float
    #: Position accuracy, 0 = low (> 10m), 1 = high (≤ 10m)
    accuracy: bool
    #: Receiver autonomous integrity monitoring (RAIM) flag of the electronic position fixing device.
    raim: bool
    #: UTC second when the report was generated by the EPFS (0-59).
    #:
    #: 60: timestamp not available, default
    #:
    #: 61: positioning system in manual input mode
    #:
    #: 62: electronic position fixing system operates in estimated (dead reckoning) mode
    #:
    #: 63: positioning system is inoperative
    seconds: int
    #: Course over Ground in radians, precision 0.0001rad
    cog: float
    #: Speed over Ground in meters per second, precision 0.01m/s
    sog: float
    #: AIS Transceiver Information, see type
    ais_transceiver_information: types.N2kAISTransceiverInformation
    #: Compass heading
    heading: float
    #: Class B unit flag, see type
    unit: types.N2kAISUnit
    #: Class B display flag
    display: bool
    #: Class B DSC flag
    dsc: bool
    #: Class B band flag
    band: bool
    #: Class B Message22 flag
    msg22: bool
    #: Station Operating Mode flag, see type
    mode: types.N2kAISMode
    #: Communication State Selector flag
    state: bool
    #: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
    #: for different messages to indicate that they are measured at same time
    sid: int = 0xFF


def create_n2k_ais_class_b_position_message(data: AISClassBPositionReport) -> Message:
    """
    AIS Position Reports for Class B (PGN 129039)

    :param data: See :py:class:`AISClassBPositionReport`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.AISClassBPositionReport
    msg.priority = 4
    msg.add_byte_uint((data.repeat & 0x03) << 6 | (data.message_id & 0x3F))
    msg.add_4_byte_uint(data.user_id)
    msg.add_4_byte_double(data.longitude, 1e-7)
    msg.add_4_byte_double(data.latitude, 1e-7)
    msg.add_byte_uint(
        (data.seconds & 0x3F) << 2 | (data.raim & 0x01) << 1 | (data.accuracy & 0x01),
    )
    msg.add_2_byte_udouble(data.cog, 1e-4)
    msg.add_2_byte_udouble(data.sog, 0.01)
    msg.add_byte_uint(0xFF)  # Communication State (19 bits)
    msg.add_byte_uint(0xFF)
    msg.add_byte_uint(((data.ais_transceiver_information & 0x1F) << 3) | 0x07)
    msg.add_2_byte_udouble(data.heading, 1e-4)
    msg.add_byte_uint(0xFF)  # Regional application
    msg.add_byte_uint(
        (data.mode & 0x01) << 7
        | (data.msg22 & 0x01) << 6
        | (data.band & 0x01) << 5
        | (data.dsc & 0x01) << 4
        | (data.display & 0x01) << 3
        | (data.unit & 0x01) << 2,
    )
    msg.add_byte_uint(0xFE | (data.state & 0x01))
    msg.add_byte_uint(data.sid)
    return msg


def parse_n2k_ais_class_b_position(msg: Message) -> AISClassBPositionReport:
    """
    Parse AIS Class B Position Report information from a PGN 129039 message

    :param msg: NMEA2000 Message with PGN 129039
    :return: Object containing the parsed information
    """
    index = IntRef(0)

    vb = msg.get_byte_uint(index)
    message_id = types.N2kAISMessageID(vb & 0x3F)
    repeat = types.N2kAISRepeat((vb >> 6) & 0x03)
    user_id = msg.get_4_byte_uint(index)
    longitude = msg.get_4_byte_double(1e-7, index)
    latitude = msg.get_4_byte_double(1e-7, index)
    vb = msg.get_byte_uint(index)
    accuracy = bool(vb & 0x01)
    raim = bool((vb >> 1) & 0x01)
    seconds = (vb >> 2) & 0x3F
    cog = msg.get_2_byte_udouble(1e-4, index)
    sog = msg.get_2_byte_udouble(0.01, index)
    msg.get_byte_uint(index)  # Communication State (19 bits)
    msg.get_byte_uint(index)
    vb = msg.get_byte_uint(index)  # AIS transceiver information (5 bits)
    ais_transceiver_information = types.N2kAISTransceiverInformation((vb >> 3) & 0x1F)
    heading = msg.get_2_byte_udouble(1e-4, index)
    msg.get_byte_uint(index)  # Regional application
    vb = msg.get_byte_uint(index)
    unit = types.N2kAISUnit((vb >> 2) & 0x01)
    display = bool((vb >> 3) & 0x01)
    dsc = bool((vb >> 4) & 0x01)
    band = bool((vb >> 5) & 0x01)
    msg22 = bool((vb >> 6) & 0x01)
    mode = types.N2kAISMode((vb >> 7) & 0x01)
    vb = msg.get_byte_uint(index)
    state = bool(vb & 0x01)
    sid = msg.get_byte_uint(index)

    return AISClassBPositionReport(
        message_id=message_id,
        repeat=repeat,
        user_id=user_id,
        longitude=longitude,
        latitude=latitude,
        accuracy=accuracy,
        raim=raim,
        seconds=seconds,
        cog=cog,
        sog=sog,
        ais_transceiver_information=ais_transceiver_information,
        heading=heading,
        unit=unit,
        display=display,
        dsc=dsc,
        band=band,
        msg22=msg22,
        mode=mode,
        state=state,
        sid=sid,
    )


# AIS Aids to Navigation (AtoN) Report (PGN 129041)
@dataclass(frozen=True, kw_only=True)
class AISAtoNReportData:
    """Data for AIS Aids to Navigation (AtoN) Report Message (PGN 129041)"""

    #: Message Type ID according to https://www.itu.int/rec/R-REC-M.1371
    message_id: types.N2kAISMessageID
    #: Repeat indicator, Used by the repeater to indicate how many times a message has been repeated.
    repeat: types.N2kAISRepeat
    #: MMSI Number (Maritime Mobile Service Identity, 9 digits)
    user_id: int
    #: Latitude in degrees, precision approx 1.1cm (1e-7 deg)
    latitude: float
    #: Longitude in degrees, precision approx 1.1cm at the equator (1e-7 deg)
    longitude: float
    #: Position accuracy, 0 = low (> 10m), 1 = high (≤ 10m)
    accuracy: bool
    #: Receiver autonomous integrity monitoring (RAIM) flag of the electronic position fixing device.
    raim: bool
    #: UTC second when the report was generated by the EPFS (0-59).
    #:
    #: 60: timestamp not available, default
    #:
    #: 61: positioning system in manual input mode
    #:
    #: 62: electronic position fixing system operates in estimated (dead reckoning) mode
    #:
    #: 63: positioning system is inoperative
    seconds: int
    #: Structure Length/Diameter in meters
    length: float
    #: Structure Beam/Diameter in meters
    beam: float
    #: Position Reference Point from Starboard Structure Edge/Radius
    position_reference_starboard: float
    #: Position Reference Point from True North facing Structure Edge/Radius
    position_reference_true_north: float
    #: Aid to Navigation (AtoN) Type, see type
    a_to_n_type: types.N2kAISAtoNType
    #: Off Position Indicator. For floating AtoN only
    #:
    #: 0: on position
    #:
    #: 1: off position
    #:
    #: Note: This flag should only be considered valid by receiving station, if the AtoN is a floatation aid,
    #: and if the time since the report has been generated is <= 59.
    off_position_reference_indicator: bool
    #: Virtual AtoN Flag
    #:
    #: 0: default = real AtoN at indicated position
    #:
    #: 1: virtual AtoN, does not physically exist.
    virtual_a_to_n_flag: bool
    #: Assigned Mode Flag
    #:
    #: 0: default = Station operating in autonomous and continuous mode
    #:
    #: 1: Station operating in assigned mode
    assigned_mode_flag: bool
    #: Type of electronic position fixing device, see type
    gnss_type: types.N2kGNSSType
    #: AtoN Status byte. Reserved for the indication of the AtoN status.
    a_to_n_status: int
    #: AIS Transceiver Information, see type.
    n2k_ais_transceiver_information: types.N2kAISTransceiverInformation
    #: Name of the AtoN Object, according to https://www.itu.int/rec/R-REC-M.1371
    a_to_n_name: str | None


def create_n2k_ais_aids_to_navigation_report_message(
    data: AISAtoNReportData,
) -> Message:
    """
    AIS Aids to Navigation (AtoN) Report (PGN 129041)

    :param data: See :py:class:`AISAtoNReportData`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.AISAidsToNavigationReport
    msg.priority = 4
    msg.add_byte_uint((data.repeat & 0x03) << 6 | data.message_id & 0x3F)
    msg.add_4_byte_uint(data.user_id)
    msg.add_4_byte_double(data.longitude, 1e-7)
    msg.add_4_byte_double(data.latitude, 1e-7)
    msg.add_byte_uint(
        (data.seconds & 0x3F) << 2 | (data.raim & 0x01) << 1 | (data.accuracy & 0x01),
    )
    msg.add_2_byte_udouble(data.length, 0.1)
    msg.add_2_byte_udouble(data.beam, 0.1)
    msg.add_2_byte_udouble(data.position_reference_starboard, 0.1)
    msg.add_2_byte_udouble(data.position_reference_true_north, 0.1)
    msg.add_byte_uint(
        (data.assigned_mode_flag & 0x01) << 7
        | (data.virtual_a_to_n_flag & 0x01) << 6
        | (data.off_position_reference_indicator & 0x01) << 5
        | (data.a_to_n_type & 0x1F),
    )
    msg.add_byte_uint(0xE0 | (data.gnss_type & 0x0F) << 1)
    msg.add_byte_uint(data.a_to_n_status)
    msg.add_byte_uint(0xE0 | (data.n2k_ais_transceiver_information & 0x1F))
    a_to_n_name = with_fallback(data.a_to_n_name, "")
    name_max_length = 34
    if len(a_to_n_name) > name_max_length:
        raise ValueError
    msg.add_var_str(a_to_n_name)

    return msg


def parse_n2k_ais_aids_to_navigation_report(msg: Message) -> AISAtoNReportData:
    """
    Parse AIS Aids to Navigation (AtoN) Report information from a PGN 129041 message

    :param msg: NMEA2000 Message with PGN 129041
    :return: Object containing the parsed information
    """
    index = IntRef(0)
    vb = msg.get_byte_uint(index)
    message_id = types.N2kAISMessageID(vb & 0x3F)
    repeat = types.N2kAISRepeat((vb >> 6) & 0x03)
    user_id = msg.get_4_byte_uint(index)
    longitude = msg.get_4_byte_double(1e-7, index)
    latitude = msg.get_4_byte_double(1e-7, index)
    vb = msg.get_byte_uint(index)
    accuracy = bool(vb & 0x01)
    raim = bool((vb >> 1) & 0x01)
    seconds = (vb >> 2) & 0x3F
    length = msg.get_2_byte_double(0.1, index)
    beam = msg.get_2_byte_double(0.1, index)
    position_reference_starboard = msg.get_2_byte_double(0.1, index)
    position_reference_true_north = msg.get_2_byte_double(0.1, index)
    vb = msg.get_byte_uint(index)
    a_to_n_type = types.N2kAISAtoNType(vb & 0x1F)
    off_position_reference_indicator = bool((vb >> 5) & 0x01)
    virtual_a_to_n_flag = bool((vb >> 6) & 0x01)
    assigned_mode_flag = bool((vb >> 7) & 0x01)
    gnss_type = types.N2kGNSSType((msg.get_byte_uint(index) >> 1) & 0x0F)
    a_to_n_status = msg.get_byte_uint(index)
    n2k_ais_transceiver_information = types.N2kAISTransceiverInformation(
        msg.get_byte_uint(index) & 0x1F,
    )
    a_to_n_name = msg.get_var_str(index)

    return AISAtoNReportData(
        message_id=message_id,
        repeat=repeat,
        user_id=user_id,
        longitude=longitude,
        latitude=latitude,
        accuracy=accuracy,
        raim=raim,
        seconds=seconds,
        length=length,
        beam=beam,
        position_reference_starboard=position_reference_starboard,
        position_reference_true_north=position_reference_true_north,
        a_to_n_type=a_to_n_type,
        off_position_reference_indicator=off_position_reference_indicator,
        virtual_a_to_n_flag=virtual_a_to_n_flag,
        assigned_mode_flag=assigned_mode_flag,
        gnss_type=gnss_type,
        a_to_n_status=a_to_n_status,
        n2k_ais_transceiver_information=n2k_ais_transceiver_information,
        a_to_n_name=a_to_n_name,
    )


# Cross Track Error (PGN 129283)
@dataclass(frozen=True, kw_only=True)
class CrossTrackError:
    """Data for Cross Track Error Message (PGN 129283)"""

    #: CrossTrackError Mode, see type
    xte_mode: types.N2kXTEMode
    #: Navigation has been terminated
    navigation_terminated: bool
    #: CrossTrackError in meters
    xte: float
    #: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
    #: for different messages to indicate that they are measured at same time.
    sid: int = 0xFF


def create_n2k_cross_track_error_message(data: CrossTrackError) -> Message:
    """
    Cross Track Error (PGN 129283)

    :param data: See :py:class:`CrossTrackError`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.CrossTrackError
    msg.priority = 3
    msg.add_byte_uint(data.sid)
    msg.add_byte_uint((data.navigation_terminated & 0x01) << 6 | (data.xte_mode & 0x0F))
    msg.add_4_byte_double(data.xte, 0.01)
    msg.add_byte_uint(0xFF)  # Reserved
    msg.add_byte_uint(0xFF)  # Reserved
    return msg


def parse_n2k_cross_track_error(msg: Message) -> CrossTrackError:
    """
    Parse Cross Track Error information from a PGN 129283 message

    :param msg: NMEA2000 Message with PGN 129283
    :return: Object containing the parsed information
    """
    index = IntRef(0)

    sid = msg.get_byte_uint(index)
    vb = msg.get_byte_uint(index)
    xte_mode = types.N2kXTEMode(vb & 0x0F)
    navigation_terminated = bool((vb >> 6) & 0x01)
    xte = msg.get_4_byte_double(0.01, index)

    return CrossTrackError(
        sid=sid,
        xte_mode=xte_mode,
        navigation_terminated=navigation_terminated,
        xte=xte,
    )


# Navigation Info (PGN 129284)
@dataclass(frozen=True, kw_only=True)
class NavigationInfo:
    """Data for Navigation Info Message (PGN 129284)"""

    #: Distance to Destination Waypoint in meters (precision 1cm)
    distance_to_waypoint: float
    #: Course/Bearing Reference, see type
    bearing_reference: types.N2kHeadingReference
    #: Perpendicular Crossed
    perpendicular_crossed: bool
    #: Arrival Circle Entered
    arrival_circle_entered: bool
    #: Calculation Type, see type
    calculation_type: types.N2kDistanceCalculationType
    #: Time part of Estimated Time at Arrival in seconds since midnight
    eta_time: float
    #: Date part of Estimated Time at Arrival in Days since 1.1.1970 UTC
    eta_date: int
    #: Bearing, From Origin to Destination Waypoint
    bearing_origin_to_destination_waypoint: float
    #: Bearing, From current Position to Destination Waypoint
    bearing_position_to_destination_waypoint: float
    #: Origin Waypoint Number
    origin_waypoint_number: int
    #: Destination Waypoint Number
    destination_waypoint_number: int
    #: Destination Waypoint Latitude
    destination_latitude: float
    #: Destination Waypoint Longitude
    destination_longitude: float
    #: Waypoint Closing Velocity
    waypoint_closing_velocity: float
    #: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
    #: for different messages to indicate that they are measured at same time.
    sid: int = 0xFF


def create_n2k_navigation_info_message(data: NavigationInfo) -> Message:
    """
    # Navigation Info (PGN 129284)

    :param data: See :py:class:`NavigationInfo`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.NavigationInfo
    msg.priority = 3
    msg.add_byte_uint(data.sid)
    msg.add_4_byte_udouble(data.distance_to_waypoint, 0.01)
    msg.add_byte_uint(
        (data.calculation_type & 0x01) << 6
        | (data.arrival_circle_entered & 0x01) << 4
        | (data.perpendicular_crossed & 0x01) << 2
        | (data.bearing_reference & 0x03),
    )
    msg.add_4_byte_udouble(data.eta_time, 1e-4)
    msg.add_2_byte_uint(data.eta_date)
    msg.add_2_byte_udouble(data.bearing_origin_to_destination_waypoint, 1e-4)
    msg.add_2_byte_udouble(data.bearing_position_to_destination_waypoint, 1e-4)
    msg.add_4_byte_uint(data.origin_waypoint_number)
    msg.add_4_byte_uint(data.destination_waypoint_number)
    msg.add_4_byte_double(data.destination_latitude, 1e-7)
    msg.add_4_byte_double(data.destination_longitude, 1e-7)
    msg.add_2_byte_double(data.waypoint_closing_velocity, 0.01)

    return msg


def parse_n2k_navigation_info(msg: Message) -> NavigationInfo:
    """
    Parse Navigation Info information from a PGN 129284 message

    :param msg: NMEA2000 Message with PGN 129284
    :return: Object containing the parsed information
    """
    index = IntRef(0)
    sid = msg.get_byte_uint(index)
    distance_to_waypoint = msg.get_4_byte_udouble(0.01, index)
    vb = msg.get_byte_uint(index)
    bearing_reference = types.N2kHeadingReference(vb & 0x03)
    perpendicular_crossed = bool((vb >> 2) & 0x01)
    arrival_circle_entered = bool((vb >> 4) & 0x01)
    calculation_type = types.N2kDistanceCalculationType((vb >> 6) & 0x01)

    return NavigationInfo(
        sid=sid,
        distance_to_waypoint=distance_to_waypoint,
        bearing_reference=bearing_reference,
        perpendicular_crossed=perpendicular_crossed,
        arrival_circle_entered=arrival_circle_entered,
        calculation_type=calculation_type,
        eta_time=msg.get_4_byte_udouble(1e-4, index),
        eta_date=msg.get_2_byte_uint(index),
        bearing_origin_to_destination_waypoint=msg.get_2_byte_udouble(1e-4, index),
        bearing_position_to_destination_waypoint=msg.get_2_byte_udouble(1e-4, index),
        origin_waypoint_number=msg.get_4_byte_uint(index),
        destination_waypoint_number=msg.get_4_byte_uint(index),
        destination_latitude=msg.get_4_byte_double(1e-7, index),
        destination_longitude=msg.get_4_byte_double(1e-7, index),
        waypoint_closing_velocity=msg.get_2_byte_double(0.01, index),
    )


# Route Waypoint Information (PGN 129285)
@dataclass(frozen=True, kw_only=True)
class RouteWaypointInformation:
    """Data for Route Waypoint Information Message (PGN 129285)"""

    #: The ID of the first waypoint
    start: int
    #: Database ID
    database: int
    #: Route ID
    route: int
    #: Navigation Direction in Route, see type
    nav_direction: types.N2kNavigationDirection
    #: The name of the current route
    route_name: str
    #: Supplementary Route/WP data available
    supplementary_data: types.N2kGenericStatusPair
    #: List of waypoints to be sent with the route.
    #: Each consisting of an ID, Name, Latitude and Longitude.
    waypoints: list[types.Waypoint]


def create_n2k_route_waypoint_information_message(
    data: RouteWaypointInformation,
) -> Message:
    """
    Route Waypoint Information (PGN 129285)

    :param data: See :py:class:`RouteWaypointInformation`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.WaypointList
    msg.priority = 6

    available_data_len = (
        msg.max_data_len - 10 - len(data.route_name) - 2
    )  # Length of space not taken up by list metadata
    base_waypoint_len = (
        2 + 4 + 4 + 2
    )  # ID, Latitude, Longitude, 2 bytes per varchar string
    for i, waypoint in enumerate(data.waypoints):
        available_data_len -= base_waypoint_len + len(waypoint.name)
        if available_data_len < 0:
            error = f"Buffer size exceeded, only the first {i:d} waypoints fit in the data buffer"
            raise ValueError(error)

    msg.add_2_byte_uint(data.start)
    msg.add_2_byte_uint(len(data.waypoints))
    msg.add_2_byte_uint(data.database)
    msg.add_2_byte_uint(data.route)
    msg.add_byte_uint(
        0xE0 | (data.supplementary_data & 0x03) << 3 | (data.nav_direction & 0x07),
    )
    msg.add_var_str(data.route_name)
    msg.add_byte_uint(0xFF)  # Reserved
    for waypoint in data.waypoints:
        msg.add_2_byte_uint(waypoint.id)
        msg.add_var_str(
            waypoint.name,
        )  # TODO: How is it, that empty string is treated differently here from 130074?
        msg.add_4_byte_double(waypoint.latitude, 1e-7)
        msg.add_4_byte_double(waypoint.longitude, 1e-7)

    return msg


def parse_n2k_route_waypoint_information(msg: Message) -> RouteWaypointInformation:
    """
    Parse Route Waypoint Information from a PGN 129285 message

    :param msg: NMEA2000 Message with PGN 129285
    :return: Object containing the parsed information
    """
    index = IntRef(0)
    start = msg.get_2_byte_uint(index)
    waypoints_len = msg.get_2_byte_uint(index)
    database = msg.get_2_byte_uint(index)
    route = msg.get_2_byte_uint(index)
    vb = msg.get_byte_uint(index)
    supplementary_data = types.N2kGenericStatusPair((vb >> 3) & 0x03)
    nav_direction = types.N2kNavigationDirection(vb & 0x07)
    route_name = with_fallback(msg.get_var_str(index), "")
    msg.get_byte_uint(index)  # Reserved
    waypoints = []
    while index.value < msg.data_len:
        waypoints.append(
            types.Waypoint(
                id=msg.get_2_byte_uint(index),
                name=with_fallback(msg.get_var_str(index), ""),
                latitude=msg.get_4_byte_double(1e-7, index),
                longitude=msg.get_4_byte_double(1e-7, index),
            ),
        )
    if len(waypoints) != waypoints_len:
        raise AssertionError

    return RouteWaypointInformation(
        start=start,
        database=database,
        route=route,
        supplementary_data=supplementary_data,
        nav_direction=nav_direction,
        route_name=route_name,
        waypoints=waypoints,
    )


# GNSS DOP data (PGN 129539)
@dataclass(frozen=True, kw_only=True)
class GNSSDOPData:
    """Data for GNSS DOP Data Message (PGN 129539)"""

    #: Desired DOP Mode
    desired_mode: types.N2kGNSSDOPmode
    #: Actual DOP Mode
    actual_mode: types.N2kGNSSDOPmode
    #: Horizontal Dilution of Precision in meters
    hdop: float
    #: Vertical Dilution of Precision in meters
    vdop: float
    #: Time Dilution of Precision
    tdop: float
    #: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
    #: for different messages to indicate that they are measured at same time.
    sid: int = 0xFF


def create_n2k_gnss_dop_message(data: GNSSDOPData) -> Message:
    """
    GNSS DOP Data (PGN 129539)

    :param data: See :py:class:`GNSSDOPData`
    :return: NMEA2000 message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.GNSSDOPData
    msg.priority = 6
    msg.add_byte_uint(data.sid)
    msg.add_byte_uint(
        0xC0 | ((data.actual_mode & 0x07) << 3) | (data.desired_mode & 0x07),
    )
    msg.add_2_byte_double(data.hdop, 0.01)
    msg.add_2_byte_double(data.vdop, 0.01)
    msg.add_2_byte_double(data.tdop, 0.01)
    return msg


def parse_n2k_gnss_dop(msg: Message) -> GNSSDOPData:
    """
    Parse GNSS DOP Data information from a PGN 129539 message

    :param msg: NMEA2000 Message with PGN 129539
    :return: Object containing the parsed information
    """
    index = IntRef(0)

    sid = msg.get_byte_uint(index)
    modes = msg.get_byte_uint(index)

    return GNSSDOPData(
        sid=sid,
        desired_mode=types.N2kGNSSDOPmode(modes & 0x07),
        actual_mode=types.N2kGNSSDOPmode((modes >> 3) & 0x07),
        hdop=msg.get_2_byte_double(0.01, index),
        vdop=msg.get_2_byte_double(0.01, index),
        tdop=msg.get_2_byte_double(0.01, index),
    )


MAX_SATELLITE_INFO_COUNT: Final = 18  # Maximum amount of satellites that fit into fast packet. TODO: extend using tp message


# GNSS Satellites in View (PGN 129540)


@dataclass(frozen=True, kw_only=True)
class GNSSSatellitesInView:
    """Data for GNSS Satellites in View Message (PGN 129540)"""

    #: Range Residual Mode
    mode: types.N2kRangeResidualMode
    #: List of the info of the satellites used
    satellites: list[types.SatelliteInfo]
    #: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
    #: for different messages to indicate that they are measured at same time.
    sid: int = 0xFF


def create_n2k_gnss_satellites_in_view_message(data: GNSSSatellitesInView) -> Message:
    """
    GNSS Satellites in View (PGN 129540)

    :param data: See :py:class:`GNSSSatellitesInView`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.GNSSSatellitesInView
    msg.priority = 6
    msg.add_byte_uint(data.sid)
    msg.add_byte_uint(0xFC | (data.mode & 0x03))  # 2 bit mode, 6 bit reserved

    if len(data.satellites) > MAX_SATELLITE_INFO_COUNT:
        # TODO: Log warning
        satellites = data.satellites[:MAX_SATELLITE_INFO_COUNT]
    else:
        satellites = data.satellites
    msg.add_byte_uint(len(satellites))

    for satellite in satellites:
        msg.add_byte_uint(satellite.prn)
        msg.add_2_byte_double(satellite.elevation, 1e-4)
        msg.add_2_byte_udouble(satellite.azimuth, 1e-4)
        msg.add_2_byte_double(satellite.snr, 1e-2)
        msg.add_4_byte_double(satellite.range_residuals, 1e-5)
        msg.add_byte_uint(satellite.usage_status | 0xF0)

    return msg


def parse_n2k_gnss_satellites_in_view(msg: Message) -> GNSSSatellitesInView:
    """
    Parse GNSS Satellites in View information from a PGN 129540 message

    :param msg: NMEA2000 Message with PGN 129540
    :return: Object containing the parsed information
    """
    index = IntRef(0)

    sid = msg.get_byte_uint(index)
    mode = types.N2kRangeResidualMode(msg.get_byte_uint(index) & 0x03)
    number_of_satellites = msg.get_byte_uint(index)
    satellites = []

    if number_of_satellites > MAX_SATELLITE_INFO_COUNT:
        # TODO: Log warning
        pass
    else:
        for _i in range(number_of_satellites):
            satellites.append(
                types.SatelliteInfo(
                    prn=msg.get_byte_uint(index),
                    elevation=msg.get_2_byte_double(1e-4, index),
                    azimuth=msg.get_2_byte_udouble(1e-4, index),
                    snr=msg.get_2_byte_double(1e-2, index),
                    range_residuals=msg.get_4_byte_double(1e-5, index),
                    usage_status=types.N2kPRNUsageStatus(
                        msg.get_byte_uint(index) & 0x0F,
                    ),
                ),
            )

    return GNSSSatellitesInView(
        sid=sid,
        mode=mode,
        satellites=satellites,
    )


# AIS Class A Static Data (PGN 129794)
@dataclass(frozen=True, kw_only=True)
class AISClassAStaticData:
    """Data for AIS Class A Static Data Message (PGN 129794)"""

    #: Message Type ID according to https://www.itu.int/rec/R-REC-M.1371
    message_id: types.N2kAISMessageID
    #: Repeat indicator. Used by the repeater to indicate how many times a message has been repeated.
    #:
    #: 0-3; 0 = default; 3 = do not repeat anymore
    repeat: types.N2kAISRepeat
    #: MMSI Number (Maritime Mobile Service Identity, 9 digits)
    user_id: int
    #: Ship identification number by IMO. [1 .. 999999999]; 0: not available = default
    imo_number: int
    #: Call Sign. Max. 7 chars will be used. Input string will be converted to contain only SixBit ASCII character set (see. ITU-R M.1371-1)
    callsign: str
    #: Name of the vessel
    #:
    #: Maximum 20 * 6bit ASCII characters.
    #:
    #: For SAR aircraft it should be set to "SAR AIRCRAFT NNNNNNN" where NNNNNNN" equals the aircraft registration number.
    #:
    #: Input string will be converted to contain only SixBit ASCII character set (see. ITU-R M.1371-1)
    name: str
    #: Vessel Type.
    #:
    #: 0: not available or no ship = default
    #:
    #: 1-99: as defined in § 3.3.2
    #:
    #: 100-199: reserved, for regional use
    #:
    #: 200-255: reserved, for regional use
    #:
    #: Not applicable to SAR aircraft
    vessel_type: int
    #: Length/Diameter in meters
    length: float
    #: Beam/Diameter in meters
    beam: float
    #: Position Reference Point from Starboard
    pos_ref_stbd: float
    #: Position Reference Point from the Bow
    pos_ref_bow: float
    #: Date part of Estimated Time at Arrival in Days since 1.1.1970 UTC
    eta_date: int
    #: Time part of Estimated Time at Arrival in seconds since midnight
    eta_time: float
    #: Maximum present static draught
    draught: float
    #: Destination. Maximum of 20 6bit ASCII Characters.
    #:
    #: Input string will be converted to contain only SixBit ASCII character set (see. ITU-R M.1371-1)
    destination: str
    #: AIS Version, see type
    ais_version: types.N2kAISVersion
    #: Type of GNSS, see type
    gnss_type: types.N2kGNSSType
    #: Data terminal equipment (DTE) ready.
    #:
    #: 0: available
    #:
    #: 1: not available = default
    dte: types.N2kAISDTE
    #: AIS Transceiver Information, see type
    ais_info: types.N2kAISTransceiverInformation
    #: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
    #: for different messages to indicate that they are measured at same time
    sid: int = 0xFF


def create_n2k_ais_class_a_static_data_message(data: AISClassAStaticData) -> Message:
    """
    AIS Class A Static Data (PGN 129794)

    :param data: See :py:class:`AISClassAStaticData`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.AISClassAStaticData
    msg.priority = 6
    msg.add_byte_uint((data.repeat & 0x03) << 6 | (data.message_id & 0x3F))
    msg.add_4_byte_uint(data.user_id)
    msg.add_4_byte_uint(data.imo_number)
    msg.add_ais_str(data.callsign, 7)
    msg.add_ais_str(data.name, 20)
    msg.add_byte_uint(data.vessel_type)
    msg.add_2_byte_double(data.length, 0.1)
    msg.add_2_byte_double(data.beam, 0.1)
    msg.add_2_byte_double(data.pos_ref_stbd, 0.1)
    msg.add_2_byte_double(data.pos_ref_bow, 0.1)
    msg.add_2_byte_uint(data.eta_date)
    msg.add_4_byte_udouble(data.eta_time, 1e-4)
    msg.add_2_byte_double(data.draught, 0.01)
    msg.add_ais_str(data.destination, 20)
    msg.add_byte_uint(
        (data.dte & 0x01) << 6
        | (data.gnss_type & 0x0F) << 2
        | (data.ais_version & 0x03),
    )
    msg.add_byte_uint(0xE0 | (data.ais_info & 0x1F))
    msg.add_byte_uint(data.sid)

    return msg


def parse_n2k_ais_class_a_static_data(msg: Message) -> AISClassAStaticData:
    """
    Parse AIS Class A Static Data information from a PGN 129794 message

    :param msg: NMEA2000 Message with PGN 129794
    :return: Object containing the parsed information
    """
    index = IntRef(0)
    vb = msg.get_byte_uint(index)
    message_id = types.N2kAISMessageID(vb & 0x3F)
    repeat = types.N2kAISRepeat((vb >> 6) & 0x03)
    user_id = msg.get_4_byte_uint(index)
    imo_number = msg.get_4_byte_uint(index)
    callsign = msg.get_str(7, index)
    name = msg.get_str(20, index)
    vessel_type = msg.get_byte_uint(index)
    length = msg.get_2_byte_double(0.1, index)
    beam = msg.get_2_byte_double(0.1, index)
    pos_ref_stbd = msg.get_2_byte_double(0.1, index)
    pos_ref_bow = msg.get_2_byte_double(0.1, index)
    eta_date = msg.get_2_byte_uint(index)
    eta_time = msg.get_4_byte_udouble(1e-4, index)
    draught = msg.get_2_byte_double(0.01, index)
    destination = msg.get_str(20, index)
    vb = msg.get_byte_uint(index)
    ais_version = types.N2kAISVersion(vb & 0x03)
    gnss_type = types.N2kGNSSType((vb >> 2) & 0x0F)
    dte = types.N2kAISDTE((vb >> 6) & 0x1F)
    ais_info = types.N2kAISTransceiverInformation(msg.get_byte_uint(index) & 0x1F)
    sid = msg.get_byte_uint(index)

    return AISClassAStaticData(
        message_id=message_id,
        repeat=repeat,
        user_id=user_id,
        imo_number=imo_number,
        callsign=callsign,
        name=name,
        vessel_type=vessel_type,
        length=length,
        beam=beam,
        pos_ref_stbd=pos_ref_stbd,
        pos_ref_bow=pos_ref_bow,
        eta_date=eta_date,
        eta_time=eta_time,
        draught=draught,
        destination=destination,
        ais_version=ais_version,
        gnss_type=gnss_type,
        dte=dte,
        ais_info=ais_info,
        sid=sid,
    )


# AIS CLass B Static Data part A (PGN 129809)
@dataclass(frozen=True, kw_only=True)
class AISClassBStaticDataPartA:
    """Data for AIS Class B Static Data Part A Message (PGN 129809)"""

    #: Message Type ID according to https://www.itu.int/rec/R-REC-M.1371
    message_id: types.N2kAISMessageID
    #: Repeat indicator. Used by the repeater to indicate how many times a message has been repeated.
    #:
    #: 0-3; 0 = default; 3 = do not repeat anymore
    repeat: types.N2kAISRepeat
    #: MMSI Number (Maritime Mobile Service Identity, 9 digits)
    user_id: int
    #: Name of the vessel
    #:
    #: Maximum 20 characters.
    #:
    #: For SAR aircraft it should be set to "SAR AIRCRAFT NNNNNNN" where NNNNNNN" equals the aircraft registration number.
    #:
    #: Input string will be converted to contain only SixBit ASCII character set (see. ITU-R M.1371-1)
    name: str
    #: AIS Transceiver Information, see type
    ais_info: types.N2kAISTransceiverInformation
    #: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
    #: for different messages to indicate that they are measured at same time
    sid: int = 0xFF


def create_n2k_ais_class_b_static_data_part_a_message(
    data: AISClassBStaticDataPartA,
) -> Message:
    """
    AIS Class B Static Data part A (PGN 129809)

    :param data: See :py:class:`AISClassBStaticDataPartA`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.AISClassBStaticDataPartA
    msg.priority = 6
    msg.add_byte_uint((data.repeat & 0x03) << 6 | (data.message_id & 0x3F))
    msg.add_4_byte_uint(data.user_id)
    msg.add_ais_str(data.name, 20)
    msg.add_byte_uint(0xE0 | (data.ais_info & 0x1F))  # AIS Transceiver info + reserved
    msg.add_byte_uint(data.sid)  # SID

    return msg


def parse_n2k_ais_class_b_static_data_part_a(msg: Message) -> AISClassBStaticDataPartA:
    """
    Parse AIS Class B Static Data Part A information from a PGN 129809 message

    :param msg: NMEA2000 Message with PGN 129809
    :return: Object containing the parsed information
    """
    index = IntRef(0)
    vb = msg.get_byte_uint(index)
    message_id = types.N2kAISMessageID(vb & 0x3F)
    repeat = types.N2kAISRepeat((vb >> 6) & 0x03)
    user_id = msg.get_4_byte_uint(index)
    name = msg.get_str(20, index)
    vb = msg.get_byte_uint(index)
    ais_info = types.N2kAISTransceiverInformation(vb & 0x1F)
    sid = msg.get_byte_uint(index)

    return AISClassBStaticDataPartA(
        message_id=message_id,
        repeat=repeat,
        user_id=user_id,
        name=name,
        ais_info=ais_info,
        sid=sid,
    )


# AIS CLass B Static Data part B (PGN 129810)
@dataclass(frozen=True, kw_only=True)
class AISClassBStaticDataPartB:
    """Data for AIS Class B Static Data Part B Message (PGN 129810)"""

    #: Message Type ID according to https://www.itu.int/rec/R-REC-M.1371
    message_id: types.N2kAISMessageID
    #: Repeat indicator. Used by the repeater to indicate how many times a message has been repeated.
    #:
    #: 0-3; 0 = default; 3 = do not repeat anymore
    repeat: types.N2kAISRepeat
    #: MMSI Number (Maritime Mobile Service Identity, 9 digits)
    user_id: int
    #: Vessel Type.
    #:
    #: 0: not available or no ship = default
    #:
    #: 1-99: as defined in § 3.3.2
    #:
    #: 100-199: reserved, for regional use
    #:
    #: 200-255: reserved, for regional use
    #:
    #: Not applicable to SAR aircraft
    vessel_type: int
    #: Unique identification of the Unit by a number as defined by the manufacturer.
    #:
    #: Input string will be converted to contain only SixBit ASCII character set (see. ITU-R M.1371-1)
    vendor: str
    #: Call Sign. Max. 7 chars will be used. Input string will be converted to contain only SixBit ASCII character set (see. ITU-R M.1371-1)
    callsign: str
    #: Length/Diameter in meters
    length: float
    #: Beam/Diameter in meters
    beam: float
    #: Position Reference Point from Starboard
    pos_ref_stbd: float
    #: Position Reference Point from the Bow
    pos_ref_bow: float
    #: MMSI of the mothership
    mothership_id: int
    #: AIS Transceiver Information, see type
    ais_info: types.N2kAISTransceiverInformation
    #: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
    #: for different messages to indicate that they are measured at same time
    sid: int = 0xFF


def create_n2k_ais_class_b_static_data_part_b_message(
    data: AISClassBStaticDataPartB,
) -> Message:
    """
    AIS CLass B Static Data part B (PGN 129810)

    :param data: See :py:class:`AISClassBStaticDataPartB`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.AISClassBStaticDataPartB
    msg.priority = 6
    msg.add_byte_uint((data.repeat & 0x03) << 6 | (data.message_id & 0x3F))
    msg.add_4_byte_uint(data.user_id)
    msg.add_byte_uint(data.vessel_type)
    msg.add_ais_str(data.vendor, 7)
    msg.add_ais_str(data.callsign, 7)
    msg.add_2_byte_udouble(data.length, 0.1)
    msg.add_2_byte_udouble(data.beam, 0.1)
    msg.add_2_byte_udouble(data.pos_ref_stbd, 0.1)
    msg.add_2_byte_udouble(data.pos_ref_bow, 0.1)
    msg.add_4_byte_uint(data.mothership_id)
    msg.add_byte_uint(0x03)  # Reserved + AIS spare
    msg.add_byte_uint(0xE0 | (data.ais_info & 0x1F))  # AIS Transceiver info + reserved
    msg.add_byte_uint(data.sid)  # SID

    return msg


def parse_n2k_ais_class_b_static_data_part_b(msg: Message) -> AISClassBStaticDataPartB:
    """
    Parse AIS Class B Static Data Part B information from a PGN 129810 message

    :param msg: NMEA2000 Message with PGN 129810
    :return: Object containing the parsed information
    """
    index = IntRef(0)
    vb = msg.get_byte_uint(index)
    message_id = types.N2kAISMessageID(vb & 0x3F)
    repeat = types.N2kAISRepeat((vb >> 6) & 0x03)
    user_id = msg.get_4_byte_uint(index)
    vessel_type = msg.get_byte_uint(index)
    vendor = msg.get_str(7, index)
    callsign = msg.get_str(7, index)
    length = msg.get_2_byte_udouble(0.1, index)
    beam = msg.get_2_byte_udouble(0.1, index)
    pos_ref_stbd = msg.get_2_byte_udouble(0.1, index)
    pos_ref_bow = msg.get_2_byte_udouble(0.1, index)
    mothership_id = msg.get_4_byte_uint(index)
    msg.get_byte_uint(index)  # 2-reserved, 6-spare
    vb = msg.get_byte_uint(index)
    ais_info = types.N2kAISTransceiverInformation(vb & 0x1F)
    sid = msg.get_byte_uint(index)

    return AISClassBStaticDataPartB(
        message_id=message_id,
        repeat=repeat,
        user_id=user_id,
        vessel_type=vessel_type,
        vendor=vendor,
        callsign=callsign,
        length=length,
        beam=beam,
        pos_ref_stbd=pos_ref_stbd,
        pos_ref_bow=pos_ref_bow,
        mothership_id=mothership_id,
        ais_info=ais_info,
        sid=sid,
    )


# Waypoint list (PGN 130074)
@dataclass(frozen=True, kw_only=True)
class WaypointList:
    """Data for Waypoint List message (PGN 130074)"""

    #: The ID of the first waypoint
    start: int
    #: Number of valid Waypoints in the list
    num_waypoints: int
    #: Database ID
    database: int
    #: List of waypoints to be sent with the route.
    #: Each consisting of an ID, Name, Latitude and Longitude.
    waypoints: list[types.Waypoint]


def create_n2k_waypoint_list_message(
    data: WaypointList,
) -> Message:
    """
    Route and Waypoint Service - Waypoint List - Waypoint Name & Position (PGN 130074)

    :param data: See :py:class:`WaypointList`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.RouteAndWaypointServiceWPListWPNameAndPosition
    msg.priority = 7

    available_data_len = (
        msg.max_data_len - 10
    )  # Length of space not taken up by list metadata
    base_waypoint_len = (
        2 + 4 + 4 + 2
    )  # ID, Latitude, Longitude, 2 bytes per varchar string
    for i, waypoint in enumerate(data.waypoints):
        available_data_len -= base_waypoint_len + len(waypoint.name or "\x00")
        if available_data_len < 0:
            error = f"Buffer size exceeded, only the first {i:d} waypoints fit in the data buffer"
            raise ValueError(error)

    msg.add_2_byte_uint(data.start)
    msg.add_2_byte_uint(len(data.waypoints))
    msg.add_2_byte_uint(data.num_waypoints)
    msg.add_2_byte_uint(data.database)
    msg.add_byte_uint(0xFF)  # Reserved
    msg.add_byte_uint(0xFF)  # Reserved

    for waypoint in data.waypoints:
        msg.add_2_byte_uint(waypoint.id)
        msg.add_var_str(
            waypoint.name or "\x00",
        )  # Instead of empty string, add a var string containing a null-byte
        msg.add_4_byte_double(waypoint.latitude, 1e-7)
        msg.add_4_byte_double(waypoint.longitude, 1e-7)

    return msg


def parse_n2k_waypoint_list(msg: Message) -> WaypointList:
    """
    Parse Waypoint List from a PGN 130074 message

    :param msg: NMEA2000 Message with PGN 130074
    :return: Object containing the parsed information
    """
    index = IntRef(0)
    start = msg.get_2_byte_uint(index)
    waypoints_len = msg.get_2_byte_uint(index)
    num_waypoints = msg.get_2_byte_uint(index)
    database = msg.get_2_byte_uint(index)
    msg.get_byte_uint(index)  # Reserved
    msg.get_byte_uint(index)  # Reserved
    waypoints = []
    while index.value < msg.data_len:
        waypoints.append(
            types.Waypoint(
                id=msg.get_2_byte_uint(index),
                name=with_fallback(msg.get_var_str(index), ""),
                latitude=msg.get_4_byte_double(1e-7, index),
                longitude=msg.get_4_byte_double(1e-7, index),
            ),
        )
    if len(waypoints) != waypoints_len:
        raise AssertionError

    return WaypointList(
        start=start,
        num_waypoints=num_waypoints,
        database=database,
        waypoints=waypoints,
    )


# Wind Speed (PGN 130306)
@dataclass(frozen=True, kw_only=True)
class WindSpeed:
    """Data for Wind Speed message (PGN 130306)"""

    #: Wind Speed in meters per second
    wind_speed: float
    #: Wind Angle in radians
    wind_angle: float
    #: Wind Reference. Can be e.g. Theoretical Wind using True North or Magnetic North,
    #: Apparent Wind as measured, ...
    #:
    #: See :py:class:`n2k.types.N2kWindReference`
    wind_reference: types.N2kWindReference
    #: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
    #: for different messages to indicate that they are measured at same time.
    sid: int = 0xFF


def create_n2k_wind_speed_message(data: WindSpeed) -> Message:
    """
    Wind Speed (PGN 130306)

    :param data: See :py:class:`WindSpeed`
    :return: NMEA2000 message ready to be sent.
    """
    msg = Message()
    msg.pgn = PGN.WindSpeed
    msg.priority = 2
    msg.add_byte_uint(data.sid)
    msg.add_2_byte_udouble(data.wind_speed, 0.01)
    msg.add_2_byte_udouble(data.wind_angle, 0.0001)
    msg.add_byte_uint(data.wind_reference)
    msg.add_byte_uint(0xFF)  # Reserved
    msg.add_byte_uint(0xFF)  # Reserved
    return msg


def parse_n2k_wind_speed(msg: Message) -> WindSpeed:
    """
    Parse heading information from a PGN 127250 message

    :param msg: NMEA2000 Message with PGN 127250
    :return: Object containing the parsed information
    """
    index = IntRef(0)
    return WindSpeed(
        sid=msg.get_byte_uint(index),
        wind_speed=msg.get_2_byte_udouble(0.01, index),
        wind_angle=msg.get_2_byte_udouble(0.0001, index),
        wind_reference=types.N2kWindReference(msg.get_byte_uint(index) & 0x07),
    )


# Outside Environmental parameters (PGN 130310)
# TODO: implement


# Environmental parameters (PGN 130311)
# TODO: implement


# Temperature [deprecated] (PGN 130312)
# TODO: implement


# Humidity (PGN 130313)
# TODO: implement


# Pressure (PGN 130314)
# TODO: implement


# Set pressure (PGN 130315)
# TODO: implement


# Temperature (PGN 130316)
# TODO: implement


# Meteorological Station Data (PGN 130323)
# TODO: implement


# Small Craft Status (Trim Tab Position) (PGN 130576)
# TODO: implement


# Direction Data (PGN 130577)
# TODO: implement


# ISO Acknowledgement (PGN 59392)
def create_n2k_pgn_iso_acknowledgement_message(
    destination: int,
    control: int,
    group_function: int,
    pgn: int,
) -> Message:
    msg = Message()
    msg.pgn = PGN.IsoAcknowledgement
    msg.priority = 6
    msg.destination = destination
    msg.add_byte_uint(control)
    msg.add_byte_uint(group_function)
    msg.add_byte_uint(0xFF)  # Reserved
    msg.add_byte_uint(0xFF)  # Reserved
    msg.add_byte_uint(0xFF)  # Reserved
    msg.add_3_byte_int(pgn)

    return msg


# ISO Address Claim (PGN 60928)
def create_n2k_iso_address_claim_message(
    destination: int,
    device_information: DeviceInformation,
) -> Message:
    return create_n2k_iso_address_claim_message_by_name(
        destination,
        device_information.name,
    )


def create_n2k_iso_address_claim_message_by_name(
    destination: int,
    name: int,
) -> Message:
    msg = Message()
    msg.pgn = PGN.IsoAddressClaim
    msg.priority = 6
    msg.destination = destination
    msg.add_uint_64(name)

    return msg


# Product Information (PGN 126996)
def create_n2k_product_information_message(
    data: types.ProductInformation,
    destination: int,
) -> Message:
    msg = Message()
    msg.pgn = PGN.ProductInformation
    msg.priority = 6
    msg.destination = destination
    msg.add_2_byte_uint(data.n2k_version)
    msg.add_2_byte_uint(data.product_code)
    msg.add_str(data.n2k_model_id, constants.MAX_N2K_MODEL_ID_LEN)
    msg.add_str(data.n2k_sw_code, constants.MAX_N2K_SW_CODE_LEN)
    msg.add_str(data.n2k_model_version, constants.MAX_N2K_MODEL_VERSION_LEN)
    msg.add_str(data.n2k_model_serial_code, constants.MAX_N2K_MODEL_SERIAL_CODE_LEN)
    msg.add_byte_uint(data.certification_level)
    msg.add_byte_uint(data.load_equivalency)

    return msg


# TODO: parser
def parse_n2k_pgn_product_information(msg: Message) -> types.ProductInformation:
    if msg.pgn != PGN.ProductInformation:
        raise ValueError

    index = IntRef(0)
    return types.ProductInformation(
        n2k_version=msg.get_2_byte_uint(index),
        product_code=msg.get_2_byte_uint(index),
        n2k_model_id=msg.get_str(constants.MAX_N2K_MODEL_ID_LEN, index),
        n2k_sw_code=msg.get_str(constants.MAX_N2K_SW_CODE_LEN, index),
        n2k_model_version=msg.get_str(constants.MAX_N2K_MODEL_VERSION_LEN, index),
        n2k_model_serial_code=msg.get_str(
            constants.MAX_N2K_MODEL_SERIAL_CODE_LEN,
            index,
        ),
        certification_level=msg.get_byte_uint(index),
        load_equivalency=msg.get_byte_uint(index),
    )


# Configuration Information (PGN: 126998)
def create_n2k_configuration_information_message(
    data: types.ConfigurationInformation,
) -> Message:
    msg = Message()

    total_len = 0
    max_len = msg.max_data_len - 6  # each field has 2 extra bytes
    man_info_len = min(
        len(data.manufacturer_information),
        constants.Max_N2K_CONFIGURATION_INFO_FIELD_LEN,
    )
    inst_desc1_len = min(
        len(data.installation_description1),
        constants.Max_N2K_CONFIGURATION_INFO_FIELD_LEN,
    )
    inst_desc2_len = min(
        len(data.installation_description2),
        constants.Max_N2K_CONFIGURATION_INFO_FIELD_LEN,
    )

    if total_len + man_info_len > max_len:
        man_info_len = max_len - total_len
    total_len += man_info_len
    if total_len + inst_desc1_len > max_len:
        inst_desc1_len = max_len - total_len
    total_len += inst_desc1_len
    if total_len + inst_desc2_len > max_len:
        inst_desc2_len = max_len - total_len
    total_len += inst_desc2_len

    msg.pgn = PGN.ConfigurationInformation
    msg.priority = 6

    # Installation Description 1
    msg.add_byte_uint(inst_desc1_len + 2)
    msg.add_byte_uint(0x01)
    msg.add_str(data.installation_description1, inst_desc1_len)

    # Installation Description 2
    msg.add_byte_uint(inst_desc2_len + 2)
    msg.add_byte_uint(0x01)
    msg.add_str(data.installation_description2, inst_desc1_len)

    # Manufacturer Information
    msg.add_byte_uint(man_info_len + 2)
    msg.add_byte_uint(0x01)
    msg.add_str(data.manufacturer_information, man_info_len)

    return msg


# TODO: parser
def parse_n2k_pgn_configuration_information(
    msg: Message,
) -> types.ConfigurationInformation:
    if msg.pgn != PGN.ConfigurationInformation:
        raise ValueError

    index = IntRef(0)

    return types.ConfigurationInformation(
        installation_description1=msg.get_var_str(index) or "",
        installation_description2=msg.get_var_str(index) or "",
        manufacturer_information=msg.get_var_str(index) or "",
    )


# ISO Request (PGN 59904)
def create_n2k_pgn_iso_request_message(destination: int, requested_pgn: int) -> Message:
    msg = Message()
    msg.pgn = PGN.IsoRequest
    msg.destination = destination
    msg.priority = 6
    msg.add_3_byte_int(requested_pgn)

    return msg


def parse_n2k_pgn_iso_request(msg: Message) -> int | None:
    iso_request_min_length = 3  # length as defined by ISO
    iso_request_max_length = 8  # extra length allowed by ported library (https://github.com/ttlappalainen/NMEA2000/commit/fffc2323e4216a547b6b490a2147e8b19bb48157)
    if iso_request_min_length <= msg.data_len <= iso_request_max_length:
        return msg.get_3_byte_uint(IntRef(0))
    return None


# enum tN2kPGNList {N2kpgnl_transmit=0, N2kpgnl_receive=1 };


# PGN List (Transmit and Receive)
def create_n2k_pgn_transmit_list_message(destination: int, pgns: list[int]) -> Message:
    raise NotImplementedError


# Heartbeat (PGN: 126993)
# time_interval_ms: between 10 and 655'320ms
def set_heartbeat(time_interval_ms: int, status_byte: int) -> Message:
    raise NotImplementedError
