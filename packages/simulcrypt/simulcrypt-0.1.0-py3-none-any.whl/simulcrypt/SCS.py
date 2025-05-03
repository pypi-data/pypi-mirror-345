# pylint: disable=C0103
from socket import socket, AF_INET, SOCK_STREAM
from select import select
from time import time, sleep

from .CWG import ControlWordGenerator as CWG
from .specification import SimulcryptSpecification as spec
from .message import SimulcryptMessage as SCM


CHANNEL_NOT_OPEN = 1
CHANNEL_SETTING_UP = 2
CHANNEL_OPEN = 3
CHANNEL_IN_ERROR = 4

STREAM_NOT_OPEN = 5
STREAM_SETTING_UP = 6
STREAM_OPEN = 7
STREAM_CLOSING = 8
STREAM_IN_ERROR = 9

INPUT_BUFFER = 16384


# pylint: disable=R0902
class SCSSimulator:
    """SimulCrypt SCS V3 simulator:

    super_CAS_id (int)     : aka Super_CAS_id
    host (str)             : ECMG hostname or IP address
    port (int)             : ECMG port number
    access_criteria (list) : list of AC to use, one per SCG
    crypto_period (int)    : custom crypto-period value, if 0 then
                             use min_CP_duration from ECMG
    timeout (int)          : timeout between connection attempts

    Implementation notes:
    - single TCP connection, single threaded logic
    - single ECM_channel_id, multiple ECM_stream_id (one per SCG/AC)
    - access_criteria_transfer_mode 0 not supported
    """

    def __init__(self,                                                                   # pylint: disable=R0913,W0102
                 super_CAS_id: int,
                 host: str,
                 port: int,
                 access_criteria: list = [],
                 crypto_period: int = 0,
                 cw_len: int = 8,
                 channel_id: int = 0,
                 timeout = 15):
        if not isinstance(super_CAS_id, int):
            raise ValueError("super_CAS_id must be int")
        if cw_len not in [8, 16]:
            raise ValueError("cw_len should be either 8 or 16")
        if not 0 <= channel_id <= 65535:
            raise ValueError("channel_id should be in 0..65535 range")
        # self.ch = Channel(id=channel_id, CAS_id=super_CAS_id, CW_len=cw_len)

        self.CAS_id = super_CAS_id
        self.ECMG_host = host
        self.ECMG_port = port
        self.access_criteria = access_criteria
        self.crypto_period = crypto_period
        self.timeout = timeout
        self.CW_len = cw_len  # 8 bytes for DVB-CSA1/CSA2, 16 for DVB-CSA3
        self.ECM_channel_id = channel_id
        self.channel_state = None
        self.stream_state = {}
        self._socket = None
        # SCS loop parameters:
        self._loop_start = 0
        self._saved_uptime = 0
        self._loop_uptime = 0
        self._send_total = 0
        self._received_total = 0
        self._errors_total = 0
        self.channel_state = CHANNEL_NOT_OPEN
        self.stream_state = {}
        self.stream_CWG = {}
        self.stream_ac_transfer_mode = {}
        self.CP_num = 1
        self.section_TSpkt_flag = None
        self.delay_start = None
        self.delay_stop = None
        self.transition_delay_start = None
        self.transition_delay_stop = None
        self.ECM_rep_period = None
        self.max_streams = None
        self.min_CP_duration = None
        self.lead_CW = None
        self.CW_per_msg = None
        self.max_comp_time = None
        self.AC_delay_start = None
        self.AC_delay_stop = None

    def run(self):
        """Connect to ECMG host, trigger SCS connection loop."""
        print(f"SCS started (super_CAS_id=0x{self.CAS_id:08x}, ECMG_host={self.ECMG_host}, port={self.ECMG_port}, "
              f"SCG_num={len(self.access_criteria)}, timeout={self.timeout}s, cp={self.crypto_period}s)")
        while True:
            try:
                self._socket = socket(AF_INET, SOCK_STREAM)
                self._socket.settimeout(self.timeout)
                self._socket.connect((self.ECMG_host, self.ECMG_port))
            except ConnectionRefusedError:
                print(f"SCS connection refused, will try again in {self.timeout} seconds...")
                sleep(self.timeout)
                continue
            except OSError as ex:
                print(f"SCS connection error ({ex}), will try again in {self.timeout} seconds...")
                sleep(self.timeout)
                continue
            else:
                print(f"SCS connected to {self.ECMG_host}:{self.ECMG_port}")
                self.scs_loop()
                self._socket.close()
                sleep(self.timeout)

    def scs_loop(self):                                                                  # pylint: disable=R0912,R0915
        """Maintain SCS channel/stream(s) open and request ECMs."""
        self._loop_start = int(time())
        self._saved_uptime = 0
        self._send_total = 0
        self._received_total = 0
        self._errors_total = 0
        self.channel_state = CHANNEL_NOT_OPEN
        self.stream_state = {}
        self.stream_CWG = {}
        self.stream_ac_transfer_mode = {}
        self.CP_num = 1
        # actual/current channel parameters
        self.section_TSpkt_flag = None
        self.delay_start = None
        self.delay_stop = None
        self.transition_delay_start = None
        self.transition_delay_stop = None
        self.ECM_rep_period = None
        self.max_streams = None
        self.min_CP_duration = None   # actual crypto-period value
        self.lead_CW = None
        self.CW_per_msg = None
        self.max_comp_time = None
        self.AC_delay_start = None
        self.AC_delay_stop = None
        for stream_id, _ in enumerate(self.access_criteria):
            self.stream_state[stream_id] = STREAM_NOT_OPEN
        self._socket.setblocking(False)
        leftover = b''
        transmit = []   # list of messages ready to send

        while True:
            self._loop_uptime = int(time()) - self._loop_start
            if self._loop_uptime > self._saved_uptime:
                if self.min_CP_duration and (self._loop_uptime % int(self.min_CP_duration/10) == 0):
                    # another crypto-period passed
                    for id_, state in self.stream_state.items():
                        if state == STREAM_OPEN:
                            transmit.append(self.cw_provision(id_))
                    self.CP_num += 1
                    if self.CP_num > 65535:
                        self.CP_num = 0
                if self._loop_uptime % 60 == 0:
                    print(f"SCS connection uptime is {self._loop_uptime}s, received: {self._received_total}, send: "
                          f"{self._send_total}, errors: {self._errors_total}")
                self._saved_uptime = self._loop_uptime
            else:
                self._saved_uptime = self._loop_uptime

            # if there is anything to send -> send
            if self._socket in select([], [self._socket], [], 0)[1]:
                if len(transmit) > 0:
                    for message in transmit:
                        print("SCS => ECMG  " + message.log_line())
                        try:
                            self._socket.sendall(message.data)
                        except ConnectionResetError:
                            print("SCS connection closed by peer")
                            return
                        self._send_total += 1
                    transmit = []

            # if ready to receive -> receive and respond
            if self._socket in select([self._socket], [], [], 0)[0]:
                try:
                    data = self._socket.recv(INPUT_BUFFER)
                except OSError as exc:
                    print(f"SCS communication error: {exc}")
                    return
                if not data:
                    print("SCS connection closed by peer")
                    return
                if leftover:
                    data = leftover + data
                    leftover = b''
                leftover_flag = False
                while True:
                    message = SCM(data)
                    if message.is_simulcrypt:
                        self._received_total += 1
                        print("SCS <= ECMG  " + message.log_line())
                        response = self.process(message)
                        if response:
                            transmit.append(response)
                        if message.leftover:
                            data = message.leftover
                            leftover_flag = True
                        else:
                            break
                    elif leftover_flag:
                        # don't fail as there might be more data available in buffer
                        leftover = data
                        break
                    else:
                        print(f"SCS received invalid message: {data.hex()}, error: {message.error_message}")
                        print("SCS closing connection")
                        return

            # prepare message(s) to transmit
            if self.channel_state == CHANNEL_NOT_OPEN:
                transmit.append(self.channel_setup())
                self.channel_state = CHANNEL_SETTING_UP

            if self.channel_state == CHANNEL_OPEN:
                stream_state_copy = self.stream_state.items()
                for num, state in stream_state_copy:
                    if state == STREAM_IN_ERROR:
                        transmit.append(self.stream_close_request(num))
                        self.stream_state[num] = STREAM_CLOSING
                    if state == STREAM_NOT_OPEN:
                        transmit.append(self.stream_setup(num))
                        self.stream_state[num] = STREAM_SETTING_UP

            sleep(0.05)

    def process(self, msg: object) -> object:
        """Process incoming message and return reply message object."""
        if self.channel_state != CHANNEL_OPEN and msg.type == spec.ECMG_CHANNEL_STATUS:
            self.section_TSpkt_flag = msg.section_TSpkt_flag
            self.delay_start = msg.delay_start
            self.delay_stop = msg.delay_stop
            self.transition_delay_start = msg.transition_delay_start if msg.has('transition_delay_start') else None
            self.transition_delay_stop = msg.transition_delay_stop if msg.has('transition_delay_stop') else None
            self.ECM_rep_period = msg.ECM_rep_period
            self.max_streams = msg.max_streams
            self.min_CP_duration = msg.min_CP_duration
            if self.crypto_period == 0:
                self.min_CP_duration = msg.min_CP_duration
            else:
                self.min_CP_duration = self.crypto_period*10
            self.lead_CW = msg.lead_CW
            self.CW_per_msg = msg.CW_per_msg
            self.max_comp_time = msg.max_comp_time
            self.AC_delay_start = msg.AC_delay_start if msg.has('AC_delay_start') else None
            self.AC_delay_stop = msg.AC_delay_stop if msg.has('AC_delay_stop') else None
            self.channel_state = CHANNEL_OPEN
            return None
        if self.channel_state == CHANNEL_OPEN and msg.type == spec.ECMG_CHANNEL_TEST:
            return self.channel_status()
        if self.channel_state == CHANNEL_OPEN and msg.type == spec.ECMG_STREAM_STATUS:
            if self.stream_state[msg.ECM_stream_id] == STREAM_SETTING_UP:
                self.stream_CWG[msg.ECM_stream_id] = CWG(self.CW_len)
                self.stream_state[msg.ECM_stream_id] = STREAM_OPEN
                self.stream_ac_transfer_mode[msg.ECM_stream_id] = msg.access_criteria_transfer_mode
                return None
        if self.channel_state == CHANNEL_OPEN and msg.type == spec.ECMG_STREAM_ERROR:
            if self.stream_state[msg.ECM_stream_id] == STREAM_OPEN:
                self.stream_state[msg.ECM_stream_id] = STREAM_IN_ERROR
                return None
        if self.channel_state == CHANNEL_OPEN and msg.type == spec.ECMG_STREAM_CLOSE_RESPONSE:
            if self.stream_state[msg.ECM_stream_id] == STREAM_CLOSING:
                self.stream_state[msg.ECM_stream_id] = STREAM_NOT_OPEN
                return None
        if self.channel_state == CHANNEL_OPEN and msg.type == spec.ECMG_STREAM_TEST:
            if self.stream_state[msg.ECM_stream_id] == STREAM_OPEN:
                return self.stream_status(msg.ECM_stream_id)
        return None

    def channel_setup(self) -> object:
        return SCM(type=spec.ECMG_CHANNEL_SETUP,
                   super_CAS_id=self.CAS_id,
                   ECM_channel_id=self.ECM_channel_id)

    def channel_status(self) -> object:
        return SCM(type=spec.ECMG_CHANNEL_STATUS,
                   ECM_channel_id=self.ECM_channel_id,
                   section_TSpkt_flag=self.section_TSpkt_flag,
                   delay_start=self.delay_start,
                   delay_stop=self.delay_stop,
                   transition_delay_start=self.transition_delay_start,
                   transition_delay_stop=self.transition_delay_stop,
                   AC_delay_start=self.AC_delay_start,
                   AC_delay_stop=self.AC_delay_stop,
                   ECM_rep_period=self.ECM_rep_period,
                   max_streams=self.max_streams,
                   min_CP_duration=self.min_CP_duration,
                   lead_CW=self.lead_CW,
                   CW_per_msg=self.CW_per_msg,
                   max_comp_time=self.max_comp_time)

    def stream_setup(self, num: int) -> object:
        return SCM(type=spec.ECMG_STREAM_SETUP,
                   ECM_channel_id=self.ECM_channel_id,
                   ECM_stream_id=num,
                   ECM_id=num,
                   nominal_CP_duration=self.min_CP_duration)

    def stream_status(self, num: int) -> object:
        return SCM(type=spec.ECMG_STREAM_STATUS,
                   ECM_channel_id=self.ECM_channel_id,
                   ECM_stream_id=num,
                   ECM_id=num,
                   access_criteria_transfer_mode=self.stream_ac_transfer_mode)

    def stream_close_request(self, num: int) -> object:
        return SCM(type=spec.ECMG_STREAM_CLOSE_REQUEST,
                   ECM_channel_id=self.ECM_channel_id,
                   ECM_stream_id=num)

    def cw_provision(self, stream_id: int) -> object:
        CP_CW_combinations = []
        for period in range(self.CW_per_msg):
            period_ = self.CP_num + period
            if period_ > 65535:
                period_ = period_ - 65536
            CP_CW_combinations.append(int.to_bytes(period_, length=2, byteorder='big') +
                                      self.stream_CWG[stream_id].cw(period_))
        return SCM(type=spec.CW_PROVISION,
                   ECM_channel_id=self.ECM_channel_id,
                   ECM_stream_id=stream_id,
                   CP_number=self.CP_num,
                   CP_CW_combination=CP_CW_combinations,
                   access_criteria=bytes.fromhex(self.access_criteria[stream_id]))
