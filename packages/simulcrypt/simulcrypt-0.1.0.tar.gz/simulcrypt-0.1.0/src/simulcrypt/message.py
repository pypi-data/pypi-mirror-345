from collections import namedtuple, Counter

from .specification import SimulcryptSpecification as spec
from .parameters import SimulcryptParameter as SCP


SIMULCRYPT_HEADER_LEN = 5       # version byte + 2 type bytes + 2 message length bytes


# pylint: disable=R0902
class SimulcryptMessage:
    """
    SimulCrypt message data access and manipulations class:

    There are two usage scenarios:

    To parse SimulCrypt data received, supply data bytes:

    data (bytes): raw data bytes of SimulCrypt message, might include
                   tail data of next message or its part from input
                   buffer.

    To build new SimulCrypt message, supply its parameters and values:

    **parameters: Simulcrypt parameters name and values to create
                  a message object for transmission, raw data stream is
                  available as .data variable
    """
    def __init__(self, data: bytes = b'', **message_params):                                   # pylint: disable=R0912
        """Create SimulCrypt message object from data stream or
        specified parameters.
        """
        self.leftover = b''          # tailing/remaining data bytes
        self.data = data             # raw data bytes
        self.parameters = []         # list of parameter tuples (type, name, value bytes)
        self.is_simulcrypt = False   # correct Simulcrypt message flag
        self.is_valid = False        # all parameters validation flag
        self.error_message = ""      # validation error hint
        self._parameter_names = []   # list of parameter names
        if data and message_params:
            raise RuntimeError("supply data bytes or message parameters")
        if data:
            if len(self.data) >= SIMULCRYPT_HEADER_LEN:
                self.version = self.data[0]
                self.type = int.from_bytes(self.data[1:3], byteorder="big")
                self.length = int.from_bytes(self.data[3:5], byteorder="big")
                # just in case data stream has multiple messages
                if len(self.data) > self.length + SIMULCRYPT_HEADER_LEN:
                    self.leftover = self.data[self.length + SIMULCRYPT_HEADER_LEN:]
                    self.data = self.data[0:self.length + SIMULCRYPT_HEADER_LEN]
                if self._data_seems_good():
                    self._parse_parameters()
                    self._check_parameters()
            else:
                self.error_message = "invalid length"
        elif message_params:
            if "version" in message_params:
                self.version = message_params["version"]
                del message_params["version"]
            else:
                self.version = 3
            if not isinstance(self.version, int):
                raise TypeError("version must be int")
            if not 1 <= self.version <= 5:
                raise ValueError("version must be in range 1-5")
            if "type" not in message_params:
                raise TypeError("message type missing")
            self.type = message_params["type"]
            del message_params["type"]
            if not isinstance(self.type, int):
                raise TypeError("message type must be int")
            if self.type not in spec.MESSAGE_TYPE:
                raise ValueError("unknown or unsupported type")
            for param in message_params:
                if param not in SCP.names(self.type):
                    raise TypeError(f"unknown parameter: {param} for message type 0x{self.type:04x} "
                                    f"({spec.MESSAGE_TYPE[self.type]})")
            self.is_simulcrypt = True
            self._make_data_stream(message_params)
            self._check_parameters()
        else:
            raise ValueError("empty data")

    def __repr__(self):
        """Simulcrypt message object representation string."""
        version = self.version if hasattr(self, "version") else "unknown"
        message_type = self.type if hasattr(self, "type") else "unknown"
        repr_string = (f"{self.__class__.__name__}(version={version}, type={message_type}, size={len(self.data)}, "
                       f"valid={self.is_valid}")
        if self.error_message:
            repr_string += f", error='{self.error_message}')"
        else:
            repr_string += ")"
        return repr_string

    def __getattr__(self, attr):
        """Return message parameter value refered by parameter name."""
        if attr in self.__dict__:
            return self.__dict__[attr]
        if "type" in self.__dict__:
            if attr in self._parameter_names:
                type_ = SCP.type_(self.type, attr)
                length = SCP.length(self.type, type_)
                values = [param.value for param in self.parameters if param.type == type_]
                if len(values) > 0:
                    if 0 < length <= 4:
                        result = [int.from_bytes(_, byteorder="big") for _ in values]
                    else:
                        result = values
                    if len(result) > 1:
                        return result
                    return result[0]
                raise RuntimeError
            raise AttributeError
        raise AttributeError

    def _data_seems_good(self) -> bool:
        """Basic check if Simulсrypt message content is valid."""
        if not 1 <= self.version <= 5:
            self.error_message = "invalid protocol version"
        elif self.length == 0:
            # message without parameter(s) isn't correct
            self.error_message = "invalid length"
        elif not len(self.data) == self.length + SIMULCRYPT_HEADER_LEN:
            self.error_message = f"invalid length (got {len(self.data)}, expect {self.length+SIMULCRYPT_HEADER_LEN})"
        elif self.type not in spec.MESSAGE_TYPE:
            self.error_message = "invalid or unsupported type"
        else:
            self.is_simulcrypt = True
        return self.is_simulcrypt

    def _check_parameters(self) -> bool:
        """Check all message parameters for compliance to particular
        Simulcrypt protocol version.
        """
        if self.version == 1:
            data_source = spec.MESSAGE_V1
        else:
            data_source = spec.MESSAGE_V2
        allowed_type = set()
        allowed_count = {}
        allowed_len = {}
        mandatory_type = set()
        for instance in data_source[self.type]:
            allowed_type.add(instance.type)
            if instance.min == 1:
                mandatory_type.add(instance.type)
            allowed_count[instance.type] = instance.max
            allowed_len[instance.type] = SCP.length(self.type, instance.type)
        # V1 CP_CW_combination is 10 bytes since CW length is 8 bytes
        if self.version == 1 and self.type == spec.CW_PROVISION and (0x0014 in allowed_len):
            allowed_len[0x0014] = 10
        # check mandatory parameters
        existing_types = [parameter.type for parameter in self.parameters]
        for param_type in mandatory_type:
            if param_type not in existing_types:
                self.error_message = (f"parameter 0x{param_type:04x} ({SCP.name(self.type, param_type)}) missing "
                                      f"in message 0x{self.type:04x} ({spec.MESSAGE_TYPE[self.type]})")
                return False
        for param in self.parameters:
            # check if allowed in that message
            if param.type not in allowed_type:
                self.error_message = (f"parameter 0x{param.type:04x} ({SCP.name(self.type, param.type)}) not allowed "
                                      f"in message 0x{self.type:04x} ({spec.MESSAGE_TYPE[self.type]})")
                return False
            # check parameter size
            if allowed_len[param.type] != 0 and allowed_len[param.type] != len(param.value):
                self.error_message = (f"invalid length of parameter 0x{param.type:04x} "
                                      f"({SCP.name(self.type, param.type)})")
                return False
        # check parameter counts
        parameter_counts = Counter(existing_types)
        for type_, count in parameter_counts.items():
            if allowed_count[type_] != 0 and allowed_count[type_] < count:
                self.error_message = f"redundant parameter 0x{type_:04x} ({SCP.name(self.type, type_)})"
                return False
        self.is_valid = True
        return self.is_valid

    def _parse_parameters(self):
        """Process valid Simulcrypt message and populate self.parameters
        dictionary with values.
        """
        SimulcryptParameter = namedtuple("SimulcryptParameter", ["type", "name", "value"])
        if self.is_simulcrypt:
            index = SIMULCRYPT_HEADER_LEN  # start byte of valid SimulCrypt parameters loop
            while index < self.length+SIMULCRYPT_HEADER_LEN:
                param_type = int.from_bytes(self.data[index:index+2], byteorder="big")
                param_name = SCP.name(self.type, param_type)
                param_len = int.from_bytes(self.data[index+2:index+4], byteorder="big")
                param_bytes = self.data[index+4:index+4 + param_len]
                param = SimulcryptParameter(param_type, param_name, param_bytes)
                if len(param_bytes) > 0:
                    self.parameters.append(param)
                    self._parameter_names.append(param_name)
                index += 4 + param_len

    def _make_data_stream(self, parameters: dict):
        """Make data stream bytes out of message parameters dict."""
        data_stream = b''
        SimulcryptParameter = namedtuple("SimulcryptParameter", ["type", "name", "value"])
        for name, value in parameters.items():
            type_ = SCP.type_(self.type, name)
            length = SCP.length(self.type, type_)
            values = value if isinstance(value, list) else [value]
            for value_ in values:
                if value_ is None:
                    continue     # won't process None
                if type(value_) not in [int, bytes]:
                    raise TypeError("parameter value must be int or bytes")
                data_stream += int.to_bytes(type_, length=2, byteorder="big")
                if length == 0:  # thus variable
                    length_ = len(value_)
                    value_bytes = value_
                else:
                    length_ = length
                    if 0 <= value_ < 256**length_:
                        value_bytes = int.to_bytes(value_, length=length_, byteorder="big")
                    else:
                        raise ValueError("parameter value is out of unsigned byte length range")
                data_stream += int.to_bytes(length_, length=2, byteorder="big")
                data_stream += value_bytes
                self.parameters.append(SimulcryptParameter(type_, name, value_bytes))
                self._parameter_names.append(name)
        self.data = int.to_bytes(self.version, length=1, byteorder="big")
        self.data += int.to_bytes(self.type, length=2, byteorder="big")
        self.data += int.to_bytes(len(data_stream), length=2, byteorder="big")
        self.data += data_stream

    def has(self, name: str) -> bool:
        """Return True if parameter name is present in the message."""
        return name in self._parameter_names

    def log_line(self) -> str:
        """Return Simulcrypt message content as a handy single line string
        useful for logging or screen output.
        """
        if not self.is_simulcrypt:
            message_tag = f"{'INVALID_MESSAGE':22}"
            if self.error_message:
                return message_tag + f"error='{self.error_message}'"
        if self.type in spec.MESSAGE_TYPE:
            message_tag = f"{spec.MESSAGE_TYPE[self.type].upper():22}"
        else:
            message_tag = f"MESSAGE_0x{self.type:04x}"
            message_tag = f"{message_tag:22}"
        type_value_pairs = []
        for param in self.parameters:
            type_value = f"{SCP.name(self.type, param.type)}="
            if param.type == 0x7001:         # error_information
                if len(param.value) <= 2:
                    type_value += f"0x{param.value.hex()}"
                else:
                    type_value += str(param.value)  # ASCII
            elif len(param.value) <= 4:      # normaly integer value
                if param.type == 0x0001:     # super_CAS_id or client_id
                    type_value += f"0x{int.from_bytes(param.value, byteorder='big'):x}"
                elif param.type == 0x000d:   # access_criteria
                    type_value += f"0x{int.from_bytes(param.value, byteorder='big'):0{len(param.value)*2}x}"
                elif param.type == 0x7000:   # error_status
                    value = int.from_bytes(param.value, byteorder="big")
                    type_value += f"0x{value:x};"
                    message = SCP.error_message(self.type, value)
                    if message:
                        type_value += f" error_message='{message}'"
                else:
                    type_value += f"{int.from_bytes(param.value, byteorder='big')}"
            elif len(param.value) <= 16:
                if param.type == 0x0014:     # CP_CW_combination
                    type_value += f"({len(param.value)} bytes)"
                else:
                    type_value += "0x" + param.value.hex()
            else:
                type_value += f"({len(param.value)} bytes)"
            type_value_pairs.append(type_value)
        if self.error_message:
            type_value_pairs.append(f"error='{self.error_message}'")
        return message_tag + ", ".join(type_value_pairs)

    def dump(self) -> str:
        """Dump message content as plain text."""
        line = ""
        if self.is_simulcrypt:
            line += f"version: {self.version}\n"
            line += f"message_type: {self.type}\n"
            line += f"message_name: {spec.MESSAGE_TYPE[self.type].upper()}\n"
            line += f"message_length: {len(self.data)}\n"
            if self.error_message:
                line += f"message_error: {self.error_message}\n"
            parameters_count = len(self.parameters)
            for num, param in enumerate(self.parameters):
                line += f"parameter_type: {param.type}\n"
                line += f"parameter_name: {SCP.name(self.type, param.type)}\n"
                line += f"parameter_length: {len(param.value)}\n"
                line += f"parameter_bytes: {param.value.hex()}"
                if num < (parameters_count-1):
                    line += "\n"
        return line

    def dump_json(self) -> str:
        """Dump message content as JSON object."""
        line = ""
        if self.is_simulcrypt:
            line += f'{{"version":{self.version},'
            line += f'"message_type":{self.type},'
            line += f'"message_name":"{spec.MESSAGE_TYPE[self.type].upper()}",'
            line += f'"message_length":{len(self.data)},'
            if self.error_message:
                line += f'"message_error":"{self.error_message}",'
            line += '"parameter_loop":['
            parameters_count = len(self.parameters)
            for num, param in enumerate(self.parameters):
                line += f'{{"type":{param.type},'
                line += f'"name":"{SCP.name(self.type, param.type)}",'
                line += f'"length":{len(param.value)},'
                line += f'"bytes":"{param.value.hex()}"}}'
                if num < (parameters_count-1):
                    line += ","
            line += "]}"
        return line
