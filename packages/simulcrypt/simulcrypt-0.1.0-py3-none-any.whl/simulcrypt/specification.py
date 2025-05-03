from collections import namedtuple
from copy import deepcopy


# pylint: disable=R0903
class SimulcryptSpecification:
    """Static class consists of Simulcrypt technical specification."""

    # For full list refer to TS 103 197 v1.5.1 (2008-10), pages 27-28
    # below is list of currently supported messages:

    ECMG_CHANNEL_SETUP = 0x0001
    ECMG_CHANNEL_TEST = 0x0002
    ECMG_CHANNEL_STATUS = 0x0003
    ECMG_CHANNEL_CLOSE = 0x0004
    ECMG_CHANNEL_ERROR = 0x0005
    EMMG_CHANNEL_SETUP = 0x0011
    EMMG_CHANNEL_TEST = 0x0012
    EMMG_CHANNEL_STATUS = 0x0013
    EMMG_CHANNEL_CLOSE = 0x0014
    EMMG_CHANNEL_ERROR = 0x0015
    ECMG_STREAM_SETUP = 0x0101
    ECMG_STREAM_TEST = 0x0102
    ECMG_STREAM_STATUS = 0x0103
    ECMG_STREAM_CLOSE_REQUEST = 0x0104
    ECMG_STREAM_CLOSE_RESPONSE = 0x0105
    ECMG_STREAM_ERROR = 0x0106
    EMMG_STREAM_SETUP = 0x0111
    EMMG_STREAM_TEST = 0x0112
    EMMG_STREAM_STATUS = 0x0113
    EMMG_STREAM_CLOSE_REQUEST = 0x0114
    EMMG_STREAM_CLOSE_RESPONSE = 0x0115
    EMMG_STREAM_ERROR = 0x0116
    STREAM_BW_REQUEST = 0x0117
    STREAM_BW_ALLOCATION = 0x0118
    CW_PROVISION = 0x0201
    ECM_RESPONSE = 0x0202
    DATA_PROVISION = 0x0211

    MESSAGE_TYPE = {
        0x0001: "channel_setup",            # ECMG <-> SCS interface
        0x0002: "channel_test",
        0x0003: "channel_status",
        0x0004: "channel_close",
        0x0005: "channel_error",
        0x0011: "channel_setup",            # EMMG <-> MUX interface
        0x0012: "channel_test",
        0x0013: "channel_status",
        0x0014: "channel_close",
        0x0015: "channel_error",
        0x0101: "stream_setup",             # ECMG <-> SCS interface
        0x0102: "stream_test",
        0x0103: "stream_status",
        0x0104: "stream_close_request",
        0x0105: "stream_close_response",
        0x0106: "stream_error",
        0x0111: "stream_setup",             # EMMG <-> MUX interface
        0x0112: "stream_test",
        0x0113: "stream_status",
        0x0114: "stream_close_request",
        0x0115: "stream_close_response",
        0x0116: "stream_error",
        0x0117: "stream_BW_request",
        0x0118: "stream_BW_allocation",
        0x0201: "CW_provision",
        0x0202: "ECM_response",
        0x0211: "data_provision"
    }

    # ECMG <-> SCS interface parameters

    ECMG_PARAMETER = {
        0x0001: "super_CAS_id",
        0x0002: "section_TSpkt_flag",
        0x0003: "delay_start",
        0x0004: "delay_stop",
        0x0005: "transition_delay_start",
        0x0006: "transition_delay_stop",
        0x0007: "ECM_rep_period",
        0x0008: "max_streams",
        0x0009: "min_CP_duration",
        0x000A: "lead_CW",
        0x000B: "CW_per_msg",
        0x000C: "max_comp_time",
        0x000D: "access_criteria",
        0x000E: "ECM_channel_id",
        0x000F: "ECM_stream_id",
        0x0010: "nominal_CP_duration",
        0x0011: "access_criteria_transfer_mode",
        0x0012: "CP_number",
        0x0013: "CP_duration",
        0x0014: "CP_CW_combination",
        0x0015: "ECM_datagram",
        0x0016: "AC_delay_start",
        0x0017: "AC_delay_stop",
        0x0018: "CW_encryption",
        0x0019: "ECM_id",
        0x7000: "error_status",
        0x7001: "error_information"
    }

    ECMG_PARAMETER_LEN = {
        0x0001: 4,
        0x0002: 1,
        0x0003: 2,
        0x0004: 2,
        0x0005: 2,
        0x0006: 2,
        0x0007: 2,
        0x0008: 2,
        0x0009: 2,
        0x000A: 1,
        0x000B: 1,
        0x000C: 2,
        0x000D: 0,  # variable
        0x000E: 2,
        0x000F: 2,
        0x0010: 2,
        0x0011: 1,
        0x0012: 2,
        0x0013: 2,
        0x0014: 0,  # 10 in V1 since CW is 8 bytes long
        0x0015: 0,
        0x0016: 2,
        0x0017: 2,
        0x0018: 0,
        0x0019: 2,
        0x7000: 2,
        0x7001: 0
    }

    ECMG_ERROR = {
        0x0001: "invalid message",
        0x0002: "unsupported protocol version",
        0x0003: "unknown message_type value",
        0x0004: "message too long",
        0x0005: "unknown Super_CAS_id value",
        0x0006: "unknown ECM_channel_id value",
        0x0007: "unknown ECM_stream_id value",
        0x0008: "too many channels on this ECMG",
        0x0009: "too many ECM streams on this channel",
        0x000A: "too many ECM streams on this ECMG",
        0x000B: "not enough control words to compute ECM",
        0x000C: "ECMG out of storage capacity",
        0x000D: "ECMG out of computational resources",
        0x000E: "unknown parameter_type value",
        0x000F: "inconsistent length for DVB parameter",
        0x0010: "missing mandatory DVB parameter",
        0x0011: "invalid value for DVB parameter",
        0x0012: "unknown ECM_id value",
        0x0013: "ECM_channel_id value already in use",
        0x0014: "ECM_stream_id value already in use",
        0x0015: "ECM_id value already in use",
        0x7000: "unknown error",
        0x7001: "unrecoverable error"
    }

    # EMMG <-> MUX interface parameters

    EMMG_PARAMETER = {
        0x0001: "client_id",
        0x0002: "section_TSpkt_flag",
        0x0003: "data_channel_id",
        0x0004: "data_stream_id",
        0x0005: "datagram",
        0x0006: "bandwidth",
        0x0007: "data_type",
        0x0008: "data_id",
        0x7000: "error_status",
        0x7001: "error_information"
    }

    EMMG_PARAMETER_LEN = {
        0x0001: 4,
        0x0002: 1,
        0x0003: 2,
        0x0004: 2,
        0x0005: 0,  # variable
        0x0006: 2,
        0x0007: 1,
        0x0008: 2,
        0x7000: 2,
        0x7001: 0
    }

    EMMG_ERROR = {
        0x0001: "invalid message",
        0x0002: "unsupported protocol version",
        0x0003: "unknown message_type value",
        0x0004: "message too long",
        0x0005: "unknown data_stream_id value",
        0x0006: "unknown data_channel_id value",
        0x0007: "too many channels on this MUX",
        0x0008: "too many data streams on this channel",
        0x0009: "too many data streams on this MUX",
        0x000A: "unknown parameter_type",
        0x000B: "inconsistent length for DVB parameter",
        0x000C: "missing mandatory DVB parameter",
        0x000D: "invalid value for DVB parameter",
        0x000E: "unknown client_id value",
        0x000F: "exceeded bandwidth",
        0x0010: "unknown data_id value",
        0x0011: "data_channel_id value already in use",
        0x0012: "data_stream_id value already in use",
        0x0013: "data_id value already in use",
        0x0014: "client_id value already in use",
        0x7000: "unknown error",
        0x7001: "unrecoverable error"
    }

    # Simulcrypt Message Parameter instance tuple:
    # min and max occurance, max 0 == multiple occurance allowed)
    SMP = namedtuple("SMP", ["type", "min", "max"])

    # Simulcrypt V1

    MESSAGE_V1 = {
        0x0001: [                   # ECMG <-> SCS CHANNEL SETUP
            SMP(0x000E, 1, 1),        # ECM_channel_id
            SMP(0x0001, 1, 1)         # super_CAS_id
        ],
        0x0002: [                   # ECMG <-> SCS CHANNEL TEST
            SMP(0x000E, 1, 1)         # ECM_channel_id
        ],
        0x0003: [                   # ECMG <-> SCS CHANNEL STATUS
            SMP(0x000E, 1, 1),        # ECM_channel_id
            SMP(0x0002, 1, 1),        # section_TSpkt_flag
            SMP(0x0016, 0, 1),        # AC_delay_start
            SMP(0x0017, 0, 1),        # AC_delay_stop
            SMP(0x0003, 1, 1),        # delay_start
            SMP(0x0004, 1, 1),        # delay_stop
            SMP(0x0005, 0, 1),        # transition_delay_start
            SMP(0x0006, 0, 1),        # transition_delay_stop
            SMP(0x0007, 1, 1),        # ECM_rep_period
            SMP(0x0008, 1, 1),        # max_streams
            SMP(0x0009, 1, 1),        # min_CP_duration
            SMP(0x000A, 1, 1),        # lead_CW
            SMP(0x000B, 1, 1),        # CW_per_msg
            SMP(0x000C, 1, 1)         # max_comp_time
        ],
        0x0004: [                   # ECMG <-> SCS CHANNEL CLOSE
            SMP(0x000E, 1, 1)         # ECM_channel_id
        ],
        0x0005: [                   # ECMG <-> SCS CHANNEL ERROR
            SMP(0x000E, 1, 1),        # ECM_channel_id
            SMP(0x7000, 1, 0),        # error_status
            SMP(0x7001, 0, 0)         # error_information
        ],
        0x0011: [                   # EMMG <-> MUX CHANNEL SETUP
            SMP(0x0001, 1, 1),        # client_id
            SMP(0x0003, 1, 1),        # data_channel_id
            SMP(0x0002, 1, 1)         # section_TSpkt_flag
        ],
        0x0012: [                   # EMMG <-> MUX CHANNEL TEST
            SMP(0x0001, 1, 1),        # client_id
            SMP(0x0003, 1, 1)         # data_channel_id
        ],
        0x0013: [                   # EMMG <-> MUX CHANNEL STATUS
            SMP(0x0001, 1, 1),        # client_id
            SMP(0x0003, 1, 1),        # data_channel_id
            SMP(0x0002, 1, 1)         # section_TSpkt_flag
        ],
        0x0014: [                   # EMMG <-> MUX CHANNEL CLOSE
            SMP(0x0001, 1, 1),        # client_id
            SMP(0x0003, 1, 1)         # data_channel_id
        ],
        0x0015: [                   # EMMG <-> MUX CHANNEL ERROR
            SMP(0x0001, 1, 1),        # client_id
            SMP(0x0003, 1, 1),        # data_channel_id
            SMP(0x7000, 1, 0),        # error_status
            SMP(0x7001, 0, 0)         # error_information
        ],
        0x0101: [                   # ECMG <-> SCS STREAM SETUP
            SMP(0x000E, 1, 1),        # ECM_channel_id
            SMP(0x000F, 1, 1),        # ECM_stream_id
            SMP(0x0010, 1, 1)         # nominal_CP_duration
        ],
        0x0102: [                   # ECMG <-> SCS STREAM TEST
            SMP(0x000E, 1, 1),        # ECM_channel_id
            SMP(0x000F, 1, 1)         # ECM_stream_id
        ],
        0x0103: [                   # ECMG <-> SCS STREAM STATUS
            SMP(0x000E, 1, 1),        # ECM_channel_id
            SMP(0x000F, 1, 1),        # ECM_stream_id
            SMP(0x0011, 1, 1)         # acccess_criteria_transfer_mode
        ],
        0x0104: [                   # ECMG <-> SCS STREAM CLOSE REQUEST
            SMP(0x000E, 1, 1),        # ECM_channel_id
            SMP(0x000F, 1, 1)         # ECM_stream_id
        ],
        0x0105: [                   # ECMG <-> SCS STREAM CLOSE RESPONSE
            SMP(0x000E, 1, 1),        # ECM_channel_id
            SMP(0x000F, 1, 1)         # ECM_stream_id
        ],
        0x0106: [                   # ECMG <-> SCS STREAM ERROR
            SMP(0x000E, 1, 1),        # ECM_channel_id
            SMP(0x000F, 1, 1),        # ECM_stream_id
            SMP(0x7000, 1, 0),        # error_status
            SMP(0x7001, 0, 0)         # error_information
        ],
        0x0111: [                   # EMMG <-> MUX STREAM SETUP
            SMP(0x0001, 1, 1),        # client_id
            SMP(0x0003, 1, 1),        # data_channel_id
            SMP(0x0004, 1, 1),        # data_stream_id
            SMP(0x0007, 1, 1)         # data_type
        ],
        0x0112: [                   # EMMG <-> MUX STREAM TEST
            SMP(0x0001, 1, 1),        # client_id
            SMP(0x0003, 1, 1),        # data_channel_id
            SMP(0x0004, 1, 1)         # data_stream_id
        ],
        0x0113: [                   # EMMG <-> MUX STREAM STATUS
            SMP(0x0001, 1, 1),        # client_id
            SMP(0x0003, 1, 1),        # data_channel_id
            SMP(0x0004, 1, 1),        # data_stream_id
            SMP(0x0007, 1, 1)         # data_type
        ],
        0x0114: [                   # EMMG <-> MUX STREAM CLOSE REQUEST
            SMP(0x0001, 1, 1),        # client_id
            SMP(0x0003, 1, 1),        # data_channel_id
            SMP(0x0004, 1, 1)         # data_stream_id
        ],
        0x0115: [                   # EMMG <-> MUX STREAM CLOSE RESPONSE
            SMP(0x0001, 1, 1),        # client_id
            SMP(0x0003, 1, 1),        # data_channel_id
            SMP(0x0004, 1, 1)         # data_stream_id
        ],
        0x0116: [                   # EMMG <-> MUX STREAM ERROR
            SMP(0x0001, 1, 1),        # client_id
            SMP(0x0003, 1, 1),        # data_channel_id
            SMP(0x0004, 1, 1),        # data_stream_id
            SMP(0x7000, 1, 0),        # error_status
            SMP(0x7001, 0, 0)         # error_information
        ],
        0x0117: [                   # EMMG <-> MUX STREAM BW REQUEST
            SMP(0x0001, 1, 1),        # client_id
            SMP(0x0003, 1, 1),        # data_channel_id
            SMP(0x0004, 1, 1),        # data_stream_id
            SMP(0x0006, 0, 1)         # bandwidth
        ],
        0x0118: [                   # EMMG <-> MUX STREAM BW ALLOCATION
            SMP(0x0001, 1, 1),        # client_id
            SMP(0x0003, 1, 1),        # data_channel_id
            SMP(0x0004, 1, 1),        # data_stream_id
            SMP(0x0006, 0, 1)         # bandwidth
        ],
        0x0201: [                   # ECMG <-> SCS CW PROVISION
            SMP(0x000E, 1, 1),        # ECM_channel_id
            SMP(0x000F, 1, 1),        # ECM_stream_id
            SMP(0x0012, 1, 1),        # CP_number
            SMP(0x0014, 1, 0),        # CP_CW_combination
            SMP(0x0013, 0, 1),        # CP_duration
            SMP(0x000D, 0, 1)         # access_criteria
        ],
        0x0202: [                   # ECMG <-> SCS ECM RESPONSE
            SMP(0x000E, 1, 1),        # ECM_channel_id
            SMP(0x000F, 1, 1),        # ECM_stream_id
            SMP(0x0012, 1, 1),        # CP_number
            SMP(0x0015, 1, 1)         # ECM_datagram
        ],
        0x0211: [                   # EMMG <-> MUX DATA PROVISION
            SMP(0x0001, 1, 1),        # client_id
            SMP(0x0003, 1, 1),        # data_channel_id
            SMP(0x0004, 1, 1),        # data_stream_id
            SMP(0x0005, 1, 0),        # datagram
        ]}

    # Simulcrypt V2+

    MESSAGE_V2 = deepcopy(MESSAGE_V1)
    # V2+: ECMG STREAM SETUP must have ECM_id parameter
    MESSAGE_V2[0x0101].append(SMP(0x0019, 1, 1))
    # V2+: ECMG STREAM STATUS must have ECM_id parameter
    MESSAGE_V2[0x0103].append(SMP(0x0019, 1, 1))
    # V2+: CW PROVISION might have an optional CW_encryption parameter
    MESSAGE_V2[0x0201].append(SMP(0x0018, 0, 1))
    # V2+: EMMG STREAM SETUP must have data_id parameter
    MESSAGE_V2[0x0111].append(SMP(0x0008, 1, 1))
    # V2+: EMMG STREAM STATUS must have data_id parameter
    MESSAGE_V2[0x0113].append(SMP(0x0008, 1, 1))
    # V2+: DATA PROVISION must have data_id parameter plus data_channel_id & data_stream_id are optional now
    MESSAGE_V2[0x0211] = [
        SMP(0x0001, 1, 1),            # client_id
        SMP(0x0003, 0, 1),            # data_channel_id (optional)
        SMP(0x0004, 0, 1),            # data_stream_id  (optional)
        SMP(0x0008, 1, 1),            # data_id         (mandatory)
        SMP(0x0005, 1, 0),            # datagram
    ]

    # Simulcrypt compatibility notes
    # ----------------------------------------------------------------------
    # V1+ : access_criteria_transfer_mode always 0 or 1
    # Vx  : CW_per_msg normally 1 or 2
    # Vx  : lead_CW normally 0 or 1
    # V1  : CW length is fixed to 8 byte so that CP_CW_combination must be 10 bytes long
    # V2+ : CP_CW_combination length is variable
    # V2+ : DATA PROVISION could be sent via UDP leaving TCP for other (control) messages
    # V1-3: section_TSpkt_flag is 0x00 (MPEG-2 section) or 0x01 (TS packet)
    # V4  : basically for PSIG <=> MUX and EIS <=> SCS context
    # V5  : section_TSpkt_flag could be 0x02 (IP datacast) (not yet implemented)
