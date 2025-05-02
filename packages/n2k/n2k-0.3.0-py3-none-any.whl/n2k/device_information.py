class DeviceInformation:
    unique_number: int  # 21 bits
    manufacturer_code: int  # 11 bits
    device_instance: int = 0  # 8 bits
    device_function: int  # 8 bits
    device_class: int  # 8 bits
    # https://github.com/ttlappalainen/NMEA2000/blob/master/src/NMEA2000.h#L133
    system_instance: int = 0  # 4 bits
    industry_group: int = 4  # 4 bits (actually 3 bits but the upper is always set)

    def __init__(
        self,
        unique_number: int,
        manufacturer_code: int,
        device_function: int,
        device_class: int,
        device_instance: int = 0,
        system_instance: int = 0,
        industry_group: int = 4,
    ) -> None:
        self.unique_number = unique_number
        self.manufacturer_code = manufacturer_code
        self.device_function = device_function
        self.device_class = device_class
        self.device_instance = device_instance
        self.system_instance = system_instance
        self.industry_group = industry_group

    @staticmethod
    def from_name(name: int) -> "DeviceInformation":
        d = DeviceInformation(0, 0, 0, 0)
        d.name = name
        return d

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

    @name.setter
    def name(self, value: int) -> None:
        self.unique_number = value & 0x1FFFFF
        self.manufacturer_code = (value >> 21) & 0x7FF
        self.device_instance = (value >> 32) & 0xFF
        self.device_function = (value >> 40) & 0xFF
        self.device_class = (value >> 48) & 0xFF
        self.system_instance = (value >> 56) & 0x0F
        self.industry_group = (value >> 60) & 0x07

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
