# pylint: disable=C0103
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from select import select
from time import time, sleep

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


class MUXSimulator:
    """Simulcrypt MUX simulator:

    client_id (int)        : aka Super_CAS_id
    port (int)             : TCP port number to listen for connection
    data_channel_id (int)  : specific value to accept or None for any
    data_stream_id (int)   : specific value to accept or None for any
    data_id (int)          : specific value to accept or None for any
    bandwidth (int)        : EMM bandwidth in kbps
    protocol_version (int) : Exact protocol version or 0

    Implementation notes:
    - only TCP for data provision and control supported (no UDP)
    - single channel and single stream communications
    - single TCP connection, single thread logic
    - EMM bandwidth is fixed per MUX instance and won't change while
      running
    """

    def __init__(self,
                 client_id: int,
                 port: int,
                 bandwidth: int,
                 data_channel_id: int = 0,
                 data_stream_id: int = 0,
                 data_id: int = 0,
                 protocol_version=0,
                 session_timeout: int = 60,
                 output_data_provision: bool = False):
        if not isinstance(client_id, int):
            raise ValueError('client_id must be int')
        # https://www.dvbservices.com/identifiers/ca_system_id
        if not 0x10000 <= client_id <= 0xaa01ffff:
            raise ValueError('invalid client_id value')
        self.client_id = client_id
        self.port = port
        self.data_channel_id = data_channel_id
        self.data_stream_id = data_stream_id
        self.data_id = data_id
        self.protocol_version = protocol_version  # protocol_version 0=accept from client, 1-5=stick to it
        self.bandwidth = bandwidth
        self.session_version = None               # session protocol version
        self.session_timeout = session_timeout
        self.section_TSpkt_flag = None
        self.data_type = None
        self.channel_state = None
        self.stream_state = None
        self.EMM_counter = 0
        self._socket = None
        self._message_counter = 0
        self._session_start_timestamp = 0
        self._session_uptime = 0
        self._saved_uptime = 0
        self._bytes_per_minute = 0                # counter for data received
        self._output_data_provision = output_data_provision
        self._connection_up = False
        self._uptime = 0

    def conn_loop(self):
        """Accept a connection on TCP port and process incoming
        Simulcrypt messages.
        """
        print(f"MUX started (client_id=0x{self.client_id:08x}, data_channel_id={self.data_channel_id}, "
              f"data_stream_id={self.data_stream_id}, data_id={self.data_id}, bandwidth={self.bandwidth})")
        self._socket = socket(AF_INET, SOCK_STREAM)
        self._socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._socket.bind(("", self.port))
        self._socket.listen(5)  # 5 is number of queued connections
        while True:
            print(f"MUX listening on port {self.port}...")
            self._socket.setblocking(True)
            (client, addr) = self._socket.accept()
            print(f"MUX got a connection from {addr[0]}:{addr[1]}")
            self._session_start_timestamp = int(time())
            self._saved_uptime = 0
            self._connection_up = True
            self._message_counter = 0
            self.EMM_counter = 0
            self.channel_state = CHANNEL_NOT_OPEN
            self.stream_state = STREAM_NOT_OPEN
            unprocessed_data = b''
            self._socket.setblocking(False)
            while True:
                if not self._connection_up:
                    break

                self._uptime = int(time()) - self._session_start_timestamp
                if self._uptime > self._saved_uptime:
                    if self._uptime % 60 == 0:
                        print(f"MUX connection uptime is {self._uptime}s; {self.EMM_counter} EMMs received at "
                              f"{self._bytes_per_minute*8/1000/60:.3f}kbps average")
                        self._bytes_per_minute = 0
                    self._saved_uptime = self._uptime
                else:
                    self._saved_uptime = self._uptime

                # drop connection if nothing received in 60s
                if (self._uptime > self.session_timeout) and (
                        self._message_counter == 0):
                    print(f"MUX got no Simulcrypt message in {self.session_timeout} seconds, closing connection")
                    client.close()
                    self._connection_up = False
                    break

                # check if data is available to retrive
                # https://docs.python.org/3.11/library/select.html
                if client in select([client], [], [], 0)[0]:
                    try:
                        data_stream = client.recv(INPUT_BUFFER)
                    except OSError as ex:
                        print(f"MUX communication error: {ex}")
                        client.close()
                        self._connection_up = False
                        break
                    else:
                        if not data_stream:
                            print("MUX connection closed by peer")
                            client.close()
                            break

                        # include bytes left from previous attempt
                        if len(unprocessed_data) > 0:
                            data_stream = unprocessed_data + data_stream
                            unprocessed_data = b''

                        tail_data_processing_flag = False
                        while True:
                            message = SCM(data_stream)
                            if message.is_simulcrypt:
                                if (message.type != spec.DATA_PROVISION) or (self._output_data_provision):
                                    print("MUX <= EMMG  " + message.log_line(), flush=True)
                                elif message.type == spec.DATA_PROVISION:
                                    print(self.EMM_counter, flush=True, end='\r')
                                self._message_counter += 1
                                if message.type == spec.EMMG_CHANNEL_CLOSE:
                                    if message.data_channel_id == self.data_channel_id:
                                        print("MUX connection closed per request")
                                        client.close()
                                        self._connection_up = False
                                        break
                                response = self.process(message)
                                if response:
                                    print("MUX => EMMG  " + response.log_line(), flush=True)
                                    client.sendall(response.data)

                                if len(message.leftover) > 0:
                                    data_stream = message.leftover
                                    tail_data_processing_flag = True
                                else:
                                    break
                            elif tail_data_processing_flag:
                                # don't fail while there is more data
                                # in recv buffer
                                unprocessed_data = data_stream
                                break
                            else:
                                print(f"MUX received invalid message: {data_stream.hex()}")
                                print(f"MUX error_message: {message.error_message}")
                                print("MUX closing connection")
                                client.close()
                                self._connection_up = False
                                break
                else:
                    sleep(0.05)

    def process(self, message: object) -> None or object:
        """Process incoming message and return reply message object."""
        if message.type == spec.EMMG_CHANNEL_CLOSE:
            self.channel_state = CHANNEL_NOT_OPEN
            self.stream_state = STREAM_NOT_OPEN

        elif self.channel_state == CHANNEL_NOT_OPEN:
            if message.type != spec.EMMG_CHANNEL_SETUP:
                error = 0x0001  # expecting channel set-up
            elif message.client_id != self.client_id:
                error = 0x000E  # unknown client_id value
            elif self.protocol_version not in [0, message.version]:
                error = 0x0002  # unsupported protocol version
            elif message.data_channel_id != self.data_channel_id:
                error = 0x0006  # unknown data_channel_id value
            elif message.section_TSpkt_flag not in (0x00, 0x01, 0x02):
                error = 0x000D  # invalid value of DVB parameter
            else:
                self.channel_state = CHANNEL_OPEN
                self.section_TSpkt_flag = message.section_TSpkt_flag
                self.session_version = message.version
                return self.channel_status()
            self.session_version = message.version
            return self.channel_error(error)

        # CHANNEL OPEN
        elif message.type == spec.EMMG_CHANNEL_TEST:
            if self.channel_state == CHANNEL_OPEN:
                return self.channel_status()
            return self.channel_error(0x0001)  # invalid message

        elif message.type == spec.EMMG_CHANNEL_CLOSE:
            if self.channel_state == CHANNEL_OPEN:
                self.channel_state = CHANNEL_NOT_OPEN
                self.stream_state = STREAM_NOT_OPEN

        elif self.stream_state == STREAM_NOT_OPEN:
            if message.type != spec.EMMG_STREAM_SETUP:
                error = 0x0001  # expecting stream set-up
            elif message.client_id != self.client_id:
                error = 0x000E  # unknown client_id value
            elif message.data_channel_id != self.data_channel_id:
                error = 0x0006  # unknown data_channel_id value
            elif message.data_stream_id != self.data_stream_id:
                error = 0x0005  # unknown data_stream_id value
            elif (self.session_version >= 2) and (message.data_id != self.data_id):
                error = 0x0010  # unknown data_id value
            else:
                self.stream_state = STREAM_OPEN
                self.data_type = message.data_type
                return self.stream_status()
            return self.stream_error(error)

        elif message.type == spec.EMMG_STREAM_TEST:
            if self.stream_state == STREAM_OPEN:
                return self.stream_status()
            return self.stream_error(0x0001)  # invalid message

        # STREAM OPEN
        elif self.stream_state == STREAM_OPEN:
            if message.type == spec.STREAM_BW_REQUEST:
                if message.client_id != self.client_id:
                    error = 0x000E  # unknown client_id value
                elif message.data_channel_id != self.data_channel_id:
                    error = 0x0006  # unknown data_channel_id value
                elif message.data_stream_id != self.data_stream_id:
                    error = 0x0005  # unknown data_stream_id value
                else:
                    return self.stream_BW_allocation()
                return self.stream_error(error)
            if message.type == spec.DATA_PROVISION:
                if message.client_id != self.client_id:
                    error = 0x000E  # unknown client_id value
                elif message.data_channel_id != self.data_channel_id:
                    error = 0x0006  # unknown data_channel_id value
                elif message.data_stream_id != self.data_stream_id:
                    error = 0x0005  # unknown data_stream_id value
                elif (self.session_version >= 2) and (message.data_id != self.data_id):
                    error = 0x0010  # unknown data_id value
                else:
                    # EMM data received
                    self.EMM_counter += 1
                    self._bytes_per_minute += len(message.datagram)
                    return b''
                return self.stream_error(error)

            if message.type == spec.EMMG_STREAM_CLOSE_REQUEST:
                self.stream_state = STREAM_NOT_OPEN
                return self.stream_close_response()

        return b''

    def channel_status(self) -> object:
        return SCM(version=self.session_version,
                   type=spec.EMMG_CHANNEL_STATUS,
                   client_id=self.client_id,
                   data_channel_id=self.data_channel_id,
                   section_TSpkt_flag=self.section_TSpkt_flag)

    def channel_error(self, error: int) -> object:
        return SCM(version=self.session_version,
                   type=spec.EMMG_CHANNEL_ERROR,
                   client_id=self.client_id,
                   data_channel_id=self.data_channel_id,
                   error_status=error)

    def stream_status(self) -> object:
        parameters = {'version': self.session_version,
                      'type': spec.EMMG_STREAM_STATUS,
                      'client_id': self.client_id,
                      'data_channel_id': self.data_channel_id,
                      'data_stream_id': self.data_stream_id,
                      'data_type': self.data_type}
        if self.session_version >= 2:
            parameters['data_id'] = self.data_id
        return SCM(**parameters)

    def stream_error(self, error: int) -> object:
        return SCM(version=self.session_version,
                   type=spec.EMMG_STREAM_ERROR,
                   client_id=self.client_id,
                   data_channel_id=self.data_channel_id,
                   data_stream_id=self.data_stream_id,
                   error_status=error)

    def stream_BW_allocation(self) -> object:
        return SCM(version=self.session_version,
                   type=spec.STREAM_BW_ALLOCATION,
                   client_id=self.client_id,
                   data_channel_id=self.data_channel_id,
                   data_stream_id=self.data_stream_id,
                   bandwidth=self.bandwidth)

    def stream_close_response(self) -> object:
        return SCM(version=self.session_version,
                   type=spec.EMMG_STREAM_CLOSE_RESPONSE,
                   client_id=self.client_id,
                   data_channel_id=self.data_channel_id,
                   data_stream_id=self.data_stream_id)
