from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class DeviceInformation:
    unique_number: int  # 21 bits
    manufacturer_code: int  # 11 bits
    device_instance: int = 0  # 8 bits
    device_function: int  # 8 bits
    device_class: int  # 8 bits
    # https://github.com/ttlappalainen/NMEA2000/blob/master/src/NMEA2000.h#L133
    system_instance: int = 0  # 4 bits
    #: 0 - Global
    #:
    #: 1 - On-Highway Equipment
    #:
    #: 2 - Agricultural and Forestry Equipment
    #:
    #: 3 - Construction Equipment
    #:
    #: 4 - Marine Equipment
    #:
    #: 5 - Industrial, Process Control, Stationary Equipment
    industry_group: int = 4  # 4 bits (actually 3 bits but the upper is always set)

    @staticmethod
    def from_name(name: int) -> "DeviceInformation":
        return DeviceInformation(
            unique_number=name & 0x1FFFFF,
            manufacturer_code=(name >> 21) & 0x7FF,
            device_instance=(name >> 32) & 0xFF,
            device_function=(name >> 40) & 0xFF,
            device_class=(name >> 48) & 0xFF,
            system_instance=(name >> 56) & 0x0F,
            industry_group=(name >> 60) & 0x07,
        )

    @property
    def name(self) -> int:
        """
        Formatting as described here:
        https://www.nmea.org/Assets/20140710%20nmea-2000-060928%20iso%20address%20claim%20pgn%20corrigendum.pdf \n
        21: Unique Number\n
        11: Manufacturer Code\n
        3: Device Instance Lower\n
        5: Device Instance Upper\n
        8: Device Function\n
        1: Reserved\n
        7: Device Class\n
        4: System Instance\n
        3: Industry Group\n
        1: Reserved\n

        :return: Values combined into NAME
        """
        return (
            (self.unique_number & 0x1FFFFF) << 0
            | (self.manufacturer_code & 0x7FF) << 21
            | (self.device_instance & 0xFF) << 32
            | (self.device_function & 0xFF) << 40
            | (self.device_class & 0xFF) << 48
            | (self.system_instance & 0x0F) << 56
            | (self.industry_group & 0x07) << 60
            | (1 << 63)
        )

    def calculated_unique_number_and_manufacturer_code(self) -> int:
        return (self.manufacturer_code & 0x7FF) << 21 | (self.unique_number & 0x1FFFFF)

    def get_device_instance_lower(self) -> int:
        return self.device_instance & 0x07

    def get_device_instance_upper(self) -> int:
        return (self.device_instance >> 3) & 0x1F

    def calculated_device_class(self) -> int:
        return (
            (self.device_class & 0x7F) << 1 >> 1
        )  # ?? in which direction should it be shifter or why shift at all?

    def calculated_industry_group_and_system_instance(self) -> int:
        return (self.industry_group << 4) | 0x80 | (self.system_instance & 0x0F)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, DeviceInformation):
            return self.name == other.name
        if isinstance(other, int):
            return self.name == other
        return False
