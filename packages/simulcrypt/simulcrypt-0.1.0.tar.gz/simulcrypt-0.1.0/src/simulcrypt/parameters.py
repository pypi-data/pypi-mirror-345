from functools import lru_cache

from .specification import SimulcryptSpecification as spec


class SimulcryptParameter:
    """Return Simulcrypt parameter name(s), values or error message
    based on the message type value.
    """

    @staticmethod
    @lru_cache
    def _ECMG_SCS_interface(message_type: int) -> bool:                                        # pylint: disable=C0103
        """Return true if message falls into ECMG <=> SCS context."""
        if 0x0001 <= message_type <= 0x0005:
            return True
        if 0x0101 <= message_type <= 0x0106:
            return True
        if 0x0201 <= message_type <= 0x0202:
            return True
        return False

    @staticmethod
    @lru_cache
    def _EMMG_MUX_interface(message_type: int) -> bool:                                        # pylint: disable=C0103
        """Return true if message falls into EMMG <=> MUX context."""
        if 0x0011 <= message_type <= 0x0015:
            return True
        if 0x0111 <= message_type <= 0x0118:
            return True
        if message_type == 0x0211:
            return True
        return False

    @staticmethod
    @lru_cache
    def name(message_type: int, param_type: int) -> str:
        """Return parameter name by its type and message type."""
        if SimulcryptParameter._ECMG_SCS_interface(message_type):
            return spec.ECMG_PARAMETER.get(param_type, f"0x{param_type:04x}")
        if SimulcryptParameter._EMMG_MUX_interface(message_type):
            return spec.EMMG_PARAMETER.get(param_type, f"0x{param_type:04x}")
        return f"0x{param_type:04x}"

    @staticmethod
    @lru_cache
    def names(message_type: int) -> list:
        """Return list of names of allowed parameters by message type."""
        if SimulcryptParameter._ECMG_SCS_interface(message_type):
            return spec.ECMG_PARAMETER.values()
        if SimulcryptParameter._EMMG_MUX_interface(message_type):
            return spec.EMMG_PARAMETER.values()
        return []

    @staticmethod
    @lru_cache
    def type_(message_type: int, param: str) -> int:
        """Return parameter type by its name and message type."""
        if SimulcryptParameter._ECMG_SCS_interface(message_type):
            data_source = spec.ECMG_PARAMETER
        elif SimulcryptParameter._EMMG_MUX_interface(message_type):
            data_source = spec.EMMG_PARAMETER
        else:
            return 0      # unknown parameter name
        if param in data_source.values():
            index = list(data_source.values()).index(param)
            key = list(data_source.keys())[index]
            return key
        return 0          # unknown parameter name

    @staticmethod
    @lru_cache
    def length(message_type: int, param: int | str) -> int:
        """Return parameter length by its type/name and message type."""
        if SimulcryptParameter._ECMG_SCS_interface(message_type):
            data_source_name = spec.ECMG_PARAMETER
            data_source_len = spec.ECMG_PARAMETER_LEN
        elif SimulcryptParameter._EMMG_MUX_interface(message_type):
            data_source_name = spec.EMMG_PARAMETER
            data_source_len = spec.EMMG_PARAMETER_LEN
        else:
            return -1     # unknown parameter
        if isinstance(param, int):
            return data_source_len[param]
        if isinstance(param, str):
            if param in data_source_name.values():
                index = list(data_source_name.values()).index(param)
                key = list(data_source_name.keys())[index]
                return data_source_len[key]
            return -1     # unknown parameter
        raise TypeError("param(eter) type must be int or str")

    @staticmethod
    @lru_cache
    def error_message(message_type: int, error_status: int) -> str:
        """Return error message string based on message type."""
        if message_type in [0x0005, 0x0106]:
            return spec.ECMG_ERROR.get(error_status, "")
        if message_type in [0x0015, 0x0116]:
            return spec.EMMG_ERROR.get(error_status, "")
        return ""
