from __future__ import annotations

from typing import Final

import n2k.device_information
import n2k.device_list
from n2k import constants
from n2k.types import ConfigurationInformation, ProductInformation
from n2k.utils import millis

MAX_NAME_REQUESTS: Final = 20
MAX_PRODUCT_INFO_REQUESTS: Final = 4
MAX_CONFIG_INFO_REQUESTS: Final = 4
MAX_PGN_LIST_REQUESTS: Final = 4
MIN_PGN_LIST_REQUEST_INTERVAL: Final = 1000


class Device:
    source: int  # uint8_t
    create_time: int  # unsigned long
    dev_i: n2k.device_information.DeviceInformation
    prod_i: ProductInformation
    prod_i_loaded: bool = False
    conf_i: ConfigurationInformation
    conf_i_loaded: bool = False
    transmit_pgns: list[int] | None = None
    receive_pgns: list[int] | None = None

    n_name_requested: int = 0  # How often we have requested the name
    prod_i_requested: int = (
        0  # Timestamp when we last requested the product information
    )
    n_prod_i_requested: int = 0  # How often we have requested the product information
    conf_i_requested: int = (
        0  # Timestamp when we last requested the configuration information
    )
    n_conf_i_requested: int = (
        0  # How often we have requested the configuration information
    )
    pgns_requested: int = 0  # Timestamp when we last requested the PGNs
    n_pgns_requested: int = 0  # How often we have requested the PGNs

    last_message_time: int

    def __init__(self, name: int, source: int = 255) -> None:
        self.source = source
        self.dev_i = n2k.device_information.DeviceInformation.from_name(name)
        self.create_time = millis()
        self.prod_i = ProductInformation(
            n2k_version=0,
            product_code=0,
            n2k_model_id="",
            n2k_sw_code="",
            n2k_model_version="",
            n2k_model_serial_code="",
            certification_level=0,
            load_equivalency=0,
        )
        self.conf_i = ConfigurationInformation(
            manufacturer_information="",
            installation_description1="",
            installation_description2="",
        )

    def should_request_name(self) -> bool:
        return self.dev_i.name == 0 and self.n_name_requested < MAX_NAME_REQUESTS

    def set_name_requested(self) -> None:
        self.n_name_requested += 1

    def clear_product_information_loaded(self) -> None:
        self.prod_i_loaded = False
        self.prod_i_requested = 0
        self.n_prod_i_requested = 0

    def should_request_product_information(self) -> bool:
        return (
            not self.prod_i_loaded
            and self.n_prod_i_requested < MAX_PRODUCT_INFO_REQUESTS
        )

    def ready_for_request_product_information(self) -> bool:
        return (
            self.should_request_product_information()
            and millis() - self.prod_i_requested
            > constants.N2K_DL_TIME_BETWEEN_PI_REQUEST
            and millis() - self.create_time > constants.N2K_DL_TIME_FOR_FIRST_REQUEST
        )

    def set_product_information_requested(self) -> None:
        self.prod_i_requested = millis()
        self.n_prod_i_requested += 1

    def clear_configuration_information_loaded(self) -> None:
        self.conf_i_loaded = False
        self.conf_i_requested = 0
        self.n_conf_i_requested = 0

    def should_request_configuration_information(self) -> bool:
        return (
            not self.conf_i_loaded
            and self.n_conf_i_requested < MAX_CONFIG_INFO_REQUESTS
        )

    def ready_for_request_configuration_information(self) -> bool:
        return (
            self.should_request_configuration_information()
            and millis() - self.conf_i_requested
            > constants.N2K_DL_TIME_BETWEEN_CI_REQUEST
            and millis() - self.create_time > constants.N2K_DL_TIME_FOR_FIRST_REQUEST
        )

    def set_configuration_information_requested(self) -> None:
        self.conf_i_requested = millis()
        self.n_conf_i_requested += 1

    def should_request_pgn_list(self) -> bool:
        return (
            self.transmit_pgns is None or self.receive_pgns is None
        ) and self.n_pgns_requested < MAX_PGN_LIST_REQUESTS

    def set_pgn_list_requested(self) -> None:
        self.pgns_requested = millis()
        self.n_pgns_requested += 1

    def ready_for_request_pgn_list(self) -> bool:
        return (
            self.should_request_pgn_list()
            and millis() - self.pgns_requested
            > constants.N2K_DL_TIME_BETWEEN_PL_REQUEST
            and millis() - self.create_time > constants.N2K_DL_TIME_FOR_FIRST_REQUEST
        )
