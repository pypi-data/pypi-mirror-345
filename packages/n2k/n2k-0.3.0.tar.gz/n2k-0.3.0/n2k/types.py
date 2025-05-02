from dataclasses import dataclass
from enum import IntEnum

import n2k.nmea2000_std_types


@dataclass
class ProductInformation:
    n2k_version: int  # unsigned short
    product_code: int  # unsigned short
    n2k_model_id: str
    n2k_sw_code: str
    n2k_model_version: str
    n2k_model_serial_code: str
    certification_level: int  # unsigned char
    load_equivalency: int  # unsigned char


@dataclass
class ConfigurationInformation:
    manufacturer_information: str
    installation_description1: str
    installation_description2: str


@dataclass
class CANSendFrame:
    id: int  # unsigned long
    length: int  # unsigned char
    buffer: bytearray  # 8 bit max


class N2kNavigationDirection(IntEnum):
    forward = 0
    reverse = 1
    reserved1 = 2
    reserved2 = 3
    reserved3 = 4
    reserved4 = 5
    error = 6
    unknown = 7


class N2kHeadingReference(IntEnum):
    true = 0
    magnetic = 1
    error = 2
    Unavailable = 3


class N2kDistanceCalculationType(IntEnum):
    GreatCircle = 0
    RhumbLine = 1


class N2kXTEMode(IntEnum):
    Autonomous = 0
    Differential = 1
    Estimated = 2
    Simulator = 3
    Manual = 4


class N2kGNSSType(IntEnum):
    GPS = 0
    GLONASS = 1
    GPS_GLONASS = 2
    GPS_SBAS_WAAS = 3
    GPS_SBAS_WAAS_GLONASS = 4
    Chayka = 5
    integrated = 6
    surveyed = 7
    Galileo = 8


class N2kGNSSMethod(IntEnum):
    NoGNSS = 0
    GNSS_fix = 1
    DGNSS = 2
    PreciseGNSS = 3
    RTKFixed = 4
    RTKFloat = 5
    Error = 14
    Unavailable = 15


class N2kGNSSDOPmode(IntEnum):
    #: 1D
    Vertical = 0
    #: 2D
    Horizontal = 1
    #: 3D
    Positional = 2
    Auto = 3
    Reserved = 4
    Reserved2 = 5
    Error = 6
    Unavailable = 7


class N2kTempSource(IntEnum):
    SeaTemperature = 0
    OutsideTemperature = 1
    InsideTemperature = 2
    EngineRoomTemperature = 3
    MainCabinTemperature = 4
    LiveWellTemperature = 5
    BaitWellTemperature = 6
    RefrigerationTemperature = 7
    HeatingSystemTemperature = 8
    DewPointTemperature = 9
    ApparentWindChillTemperature = 10
    TheoreticalWindChillTemperature = 11
    HeatIndexTemperature = 12
    FreezerTemperature = 13
    ExhaustGasTemperature = 14
    ShaftSealTemperature = 15


class N2kHumiditySource(IntEnum):
    InsideHumidity = 0
    OutsideHumidity = 1
    Undef = 0xFF


class N2kPressureSource(IntEnum):
    Atmospheric = 0
    Water = 1
    Steam = 2
    CompressedAir = 3
    Hydraulic = 4
    Filter = 5
    AltimeterSetting = 6
    Oil = 7
    Fuel = 8
    Reserved = 253
    Error = 254
    Unavailable = 255


class N2kTimeSource(IntEnum):
    GPS = 0
    GLONASS = 1
    RadioStation = 2
    LocalCesiumClock = 3
    LocalRubidiumClock = 4
    LocalCrystalClock = 5


class N2kFluidType(IntEnum):
    Fuel = 0
    Water = 1
    GrayWater = 2
    LiveWell = 3
    Oil = 4
    BlackWater = 5
    FuelGasoline = 6
    Error = 14
    Unavailable = 15


class N2kWindReference(IntEnum):
    # Details found on page 12 of https://www.rocktheboatmarinestereo.com/specs/MSNRX200I.pdf
    # Theoretical Wind (ground referenced, referenced to True North; calculated using COG/SOG)
    TrueNorth = 0
    # Theoretical Wind (ground referenced, referenced to Magnetic North; calculated using COG/SOG)
    Magnetic = 1
    # Apparent Wind (relative to the vessel centerline)
    Apparent = 2
    # Theoretical (Calculated to Centerline of the vessel, referenced to ground; calculated using COG/SOG)
    TrueBoat = 3
    # Theoretical (Calculated to Centerline of the vessel, referenced to water;
    # calculated using Heading/Speed through Water)
    TrueWater = 4
    Error = 6
    Unavailable = 7


class N2kSpeedWaterReferenceType(IntEnum):
    PaddleWheel = 0
    PitotTube = 1
    DopplerLog = 2
    Ultrasound = 3
    Electromagnetic = 4
    Error = 254
    Unavailable = 255


class N2kRudderDirectionOrder(IntEnum):
    NoDirectionOrder = 0
    MoveToStarboard = 1
    MoveToPort = 2
    Unavailable = 7


class N2kDCType(IntEnum):
    Battery = 0
    Alternator = 1
    Converter = 2
    SolarCell = 3
    WindGenerator = 4


class N2kBatType(IntEnum):
    Flooded = 0
    Gel = 1
    AGM = 2


class N2kBatEqSupport(IntEnum):
    No = 0  # No, Off, Disabled
    Yes = 1  # Yes, On, Enabled
    Error = 2  # Error
    Unavailable = 3  # Unavailable


class N2kBatChem(IntEnum):
    LeadAcid = 0
    LiIon = 1
    NiCad = 2
    Zn0 = 3
    NiMh = 4


class N2kBatNomVolt(IntEnum):
    Volt_6 = 0
    Volt_12 = 1
    Volt_24 = 2
    Volt_32 = 3
    Volt_36 = 4
    Volt_42 = 5
    Volt_48 = 6


class N2kTransmissionGear(IntEnum):
    Forward = 0
    Neutral = 1
    Reverse = 2
    Unknown = 3


class N2kAISRepeat(IntEnum):
    Initial = 0
    First = 1
    Second = 2
    Final = 3


class N2kAISVersion(IntEnum):
    ITU_R_M_1371_1 = 0
    ITU_R_M_1371_3 = 1


class N2kAISNavStatus(IntEnum):
    Under_Way_Motoring = 0
    At_Anchor = 1
    Not_Under_Command = 2
    Restricted_Maneuverability = 3
    Constrained_By_Draught = 4
    Moored = 5
    Aground = 6
    Fishing = 7
    Under_Way_Sailing = 8
    Hazardous_Material_High_Speed = 9
    Hazardous_Material_Wing_In_Ground = 10
    AIS_SART = 14


class N2kAISDTE(IntEnum):
    Ready = 0
    NotReady = 1


class N2kAISUnit(IntEnum):
    ClassB_SOTDMA = 0
    ClassB_CS = 1


class N2kAISMode(IntEnum):
    Autonomous = 0
    Assigned = 1


class N2kAISTransceiverInformation(IntEnum):
    Channel_A_VDL_reception = 0
    Channel_B_VDL_reception = 1
    Channel_A_VDL_transmission = 2
    Channel_B_VDL_transmission = 3
    Own_information_not_broadcast = 4
    Reserved = 5


class N2kAISMessageID(IntEnum):
    Scheduled_Class_A_position_report = 1
    Assigned_scheduled_Class_A_position_report = 2
    Interrogated_Class_A_position_report = 3
    Base_station_report = 4
    Static_and_voyage_related_data = 5
    Binary_addressed_message = 6
    Binary_acknowledgement = 7
    Binary_broadcast_message = 8
    Standard_SAR_aircraft_position_report = 9
    UTC_date_inquiry = 10
    UTC_date_response = 11
    Safety_related_addressed_message = 12
    Safety_related_acknowledgement = 13
    Safety_related_broadcast_message = 14
    Interrogation = 15
    Assignment_mode_command = 16
    DGNSS_broadcast_binary_message = 17
    Standard_Class_B_position_report = 18
    Extended_Class_B_position_report = 19
    Data_link_management_message = 20
    ATON_report = 21
    Channel_management = 22
    Group_assignment_command = 23
    Static_data_report = 24
    Single_slot_binary_message = 25
    Multiple_slot_binary_message = 26
    Position_report_for_long_range_applications = 27


class N2kMagneticVariation(IntEnum):
    Manual = 0
    Chart = 1
    Table = 2
    Calc = 3
    WMM2000 = 4
    WMM2005 = 5
    WMM2010 = 6
    WMM2015 = 7
    WMM2020 = 8


class N2kOnOff(IntEnum):
    Off = 0  # No, Off, Disabled
    On = 1  # Yes, On, Enabled
    Error = 2  # Error
    Unavailable = 3  # Unavailable


class N2kChargeState(IntEnum):
    Not_Charging = 0
    Bulk = 1
    Absorption = 2
    Overcharge = 3
    Equalize = 4
    Float = 5
    No_Float = 6
    Constant_VI = 7
    Disabled = 8
    Fault = 9
    Error = 14
    Unavailable = 15


class N2kChargerMode(IntEnum):
    Standalone = 0
    Primary = 1
    Secondary = 2
    Echo = 3
    Unavailable = 15


class N2kConvMode(IntEnum):
    Off = 0
    LP_Mode = 1  # Low Power Mode
    Fault = 2
    Bulk = 3
    Absorption = 4
    Float = 5
    Storage = 6
    Equalize = 7
    Passthrough = 8
    Inverting = 9
    Assisting = 10
    PSU_Mode = 11
    Hub1 = 0xFC  # In slave/DDC mode
    NotAvailable = 0xFF


class N2kRippleState(IntEnum):
    OK = 0
    Warning = 1
    High = 2  # Ripple too high
    NotAvailable = 3


class N2kDCVoltageState(IntEnum):
    OK = 0
    Warning = 1
    Low = 2  # DC Voltage too low
    NotAvailable = 3


class N2kOverloadState(IntEnum):
    OK = 0
    Warning = 1
    Overload = 2
    NotAvailable = 3


class N2kTemperatureState(IntEnum):
    OK = 0
    Warning = 1
    High = 2  # Over Temperature
    NotAvailable = 3


class N2kChargingAlgorithm(IntEnum):
    Trickle = 0
    CVCC = 1  # Constant Voltage Constant Current
    TwoStage = 2  # 2 Stage (no Float)
    ThreeStage = 3  # 3 Stage (Bulk, Absorption, Float?)
    Error = 14
    NotAvailable = 15


# Battery temperature with no temperature sensor
class N2kBattTempNoSensor(IntEnum):
    Cold = 0
    Warm = 1
    Hot = 2
    Error = 14
    NotAvailable = 15


class N2kSteeringMode(IntEnum):
    MainSteering = 0
    NonFollowUpDevice = 1
    FollowUpDevice = 2
    HeadingControlStandalone = 3
    HeadingControl = 4
    TrackControl = 5
    Unavailable = 7


class N2kTurnMode(IntEnum):
    RudderLimitControlled = 0
    TurnRateControlled = 1
    RadiusControlled = 2
    Unavailable = 7


class N2kMOBStatus(IntEnum):
    MOBEmitterActivated = 0
    ManualOnBoardMOBButtonActivation = 1
    TestMode = 2
    MOBNotActive = 3


class N2kMOBPositionSource(IntEnum):
    PositionEstimatedByVessel = 0
    PositionReportedByMOBEmitter = 1


class N2kMOBEmitterBatteryStatus(IntEnum):
    Good = 0
    Low = 1


class N2kPGNList(IntEnum):
    transmit = 0
    receive = 1


class N2kTransmissionDiscreteStatus1:
    check_temperature: int = 0
    over_temperature: int = 0
    low_oil_pressure: int = 0
    low_oil_level: int = 0
    sail_drive: int = 0

    def __init__(self, value: int = 0) -> None:
        self.status = value

    @property
    def status(self) -> int:
        return (
            self.check_temperature << 0
            | self.over_temperature << 1
            | self.low_oil_pressure << 2
            | self.low_oil_level << 3
            | self.sail_drive << 4
        )

    @status.setter
    def status(self, value: int) -> None:
        self.check_temperature = (value >> 0) & 0b1
        self.over_temperature = (value >> 1) & 0b1
        self.low_oil_pressure = (value >> 2) & 0b1
        self.low_oil_level = (value >> 3) & 0b1
        self.sail_drive = (value >> 4) & 0b1

    def __eq__(self, other: object) -> bool:
        if isinstance(other, N2kTransmissionDiscreteStatus1):
            return self.status == other.status
        if isinstance(other, int):
            return self.status == other
        return False


N2kBinaryStatus = int


# Aliases for N2K standard types
N2kEngineDiscreteStatus1 = n2k.nmea2000_std_types.N2kDD206
N2kEngineDiscreteStatus2 = n2k.nmea2000_std_types.N2kDD223

N2kGenericStatusPair = n2k.nmea2000_std_types.N2kDD002
N2kDataMode = n2k.nmea2000_std_types.N2kDD025
N2kRangeResidualMode = n2k.nmea2000_std_types.N2kDD072
N2kPRNUsageStatus = n2k.nmea2000_std_types.N2kDD124
N2kAISAtoNType = n2k.nmea2000_std_types.N2kDD305
N2kDelaySource = n2k.nmea2000_std_types.N2kDD374
N2kThrusterMotorEvents = n2k.nmea2000_std_types.N2kDD471
N2kThrusterDirectionControl = n2k.nmea2000_std_types.N2kDD473
N2kThrusterRetraction = n2k.nmea2000_std_types.N2kDD474
N2kThrusterControlEvents = n2k.nmea2000_std_types.N2kDD475
N2kWindlassMonitoringEvents = n2k.nmea2000_std_types.N2kDD477
N2kWindlassControlEvents = n2k.nmea2000_std_types.N2kDD478
N2kWindlassMotionStates = n2k.nmea2000_std_types.N2kDD480
N2kRodeTypeStates = n2k.nmea2000_std_types.N2kDD481
N2kAnchorDockingStates = n2k.nmea2000_std_types.N2kDD482
N2kWindlassOperatingEvents = n2k.nmea2000_std_types.N2kDD483
N2kWindlassDirectionControl = n2k.nmea2000_std_types.N2kDD484
N2kMotorPowerType = n2k.nmea2000_std_types.N2kDD487
N2kSpeedType = n2k.nmea2000_std_types.N2kDD488


@dataclass
class Waypoint:
    id: int
    name: str
    latitude: float
    longitude: float


@dataclass
class SatelliteInfo:
    prn: int
    elevation: float
    azimuth: float
    snr: float
    range_residuals: float
    usage_status: N2kPRNUsageStatus
