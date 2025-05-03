# Handling DVB Simulcrypt protocol messages

Pure Python library made with focus on compliance to DVB specifications.

Only these component-to-component interfaces covered:

* SCS &#8660; ECMG
* EMMG &#8660; MUX

Intended to help developing applications dealing with Simulcrypt packets. Could be useful for DigitalTV/DVB hardware
simulation, monitoring, etc. Could be used to produce Prometheus metrics out of Simulcrypt traffic capture.

## Quick start

```
$ python3
>>> from simulcrypt import SimulcryptMessage
```

How to make Simulcrypt packet object from bytes:

```
>>> message = SimulcryptMessage(bytes.fromhex('020001000e000e00020001000100044ae60000'))
>>> message
SimulcryptMessage(version=2, type=1, size=19, valid=True)
```

How to print the message content:

```
>>> message.data.hex()
'030001000e000e00020001000100044ae60000'
```
```
>>> message.log_line()
'CHANNEL_SETUP         ECM_channel_id=1, super_CAS_id=0x4ae60000'
```
```
>>> print(message.dump_json())
{"version":2,"message_type":1,"message_name":"CHANNEL_SETUP","message_length":19,
 "parameter_loop":[{"type":14,"name":"ECM_channel_id","length":2,"bytes":"0001"},{"type":1,"name":"super_CAS_id","length":4,"bytes":"4ae60000"}]}
```
```
>>> print(message.dump())
version: 2
message_type: 1
message_name: CHANNEL_SETUP
message_length: 19
parameter_type: 14
parameter_name: ECM_channel_id
parameter_length: 2
parameter_bytes: 0001
parameter_type: 1
parameter_name: super_CAS_id
parameter_length: 4
parameter_bytes: 4ae60000
```

Simulcrypt object properties and functions:

| name | type | description |
| :---  | :--- | :--- |
| SimulcryptMessage.type | int | message type value |
| SimulcryptMessage.version | int | message version value (must be from 1 to 5)|
| SimulcryptMessage.length | int | message length in bytes |
| SimulcryptMessage.data | bytes | message raw bytes |
| SimulcryptMessage.is_simulcrypt | bool | True if message seems like Simulcrypt with correct version, type and length (no checks further) |
| SimulcryptMessage.is_valid | bool | True if message is valid Simulcrypt by checking all parameters presence, count and length |
| SimulcryptMessage.parameters | list | list of message parameters namedtuple("SimulcryptParameter", ["type", "name", "value"]) |
| SimulcryptMessage.error_message | str | problem description if message isn't valid nor Simulcrypt |
| SimulcryptMessage.log_line() | function | produce one line representation of the message, useful for logging |
| SimulcryptMessage.dump() | function | output message content as plain text |
| SimulcryptMessage.dump_json() | function | output message content as JSON object |

## Advanced usage

How to create Simulcrypt message object using parameters and their values:

```
>>> from simulcrypt import SimulcryptSpecification as spec
>>> message = SimulcryptMessage(version=3, type=spec.ECMG_CHANNEL_SETUP, ECM_channel_id=1, super_CAS_id=0x4ae60000)
>>> message
SimulcryptMessage(version=3, type=1, size=19, valid=True)
>>> message.data
b'\x03\x00\x01\x00\x0e\x00\x0e\x00\x02\x00\x01\x00\x01\x00\x04J\xe6\x00\x00'
```

Parameter value could be of list type to make multiple instances. Here is example of multiple `CP_CW_combination` values in the message:

```
>>> message = SimulcryptMessage(verson=3, type=spec.CW_PROVISION, ECM_channel_id=1, ECM_stream_id=1, CP_number=0x7488,
CP_CW_combination=[bytes.fromhex('748845cbbe00000000be'), bytes.fromhex('748945cbc000000000c0')],
access_criteria=bytes.fromhex('900100060001006a0001'))
>>> message.data.hex()
'030201003c000e00020001000f000200010012000274880014000a748845cbbe00000000be0014000a748945cbc000000000c0000d000a900100060001006a0001'
```

All message types available:

| name | hex/dec. type |
| :--- | :--- |
| SimulcryptSpecification.ECMG_CHANNEL_SETUP | 0x0001 / 1 |
| SimulcryptSpecification.ECMG_CHANNEL_TEST | 0x0002 / 2 |
| SimulcryptSpecification.ECMG_CHANNEL_STATUS | 0x0003 / 3 |
| SimulcryptSpecification.ECMG_CHANNEL_CLOSE | 0x0004 / 4 |
| SimulcryptSpecification.ECMG_CHANNEL_ERROR | 0x0005 / 5 |
| SimulcryptSpecification.EMMG_CHANNEL_SETUP | 0x0011 / 17 |
| SimulcryptSpecification.EMMG_CHANNEL_TEST | 0x0012 / 18 |
| SimulcryptSpecification.EMMG_CHANNEL_STATUS | 0x0013 / 19 |
| SimulcryptSpecification.EMMG_CHANNEL_CLOSE | 0x0014 / 20 |
| SimulcryptSpecification.EMMG_CHANNEL_ERROR | 0x0015 / 21 |
| SimulcryptSpecification.ECMG_STREAM_SETUP | 0x0101 / 257 |
| SimulcryptSpecification.ECMG_STREAM_TEST | 0x0102 / 258 |
| SimulcryptSpecification.ECMG_STREAM_STATUS | 0x0103 / 259 |
| SimulcryptSpecification.ECMG_STREAM_CLOSE_REQUEST | 0x0104 / 260 |
| SimulcryptSpecification.ECMG_STREAM_CLOSE_RESPONSE | 0x0105 / 261 |
| SimulcryptSpecification.ECMG_STREAM_ERROR | 0x0106 / 262 |
| SimulcryptSpecification.EMMG_STREAM_SETUP | 0x0111 / 273 |
| SimulcryptSpecification.EMMG_STREAM_TEST | 0x0112 / 274 |
| SimulcryptSpecification.EMMG_STREAM_STATUS | 0x0113 / 275 |
| SimulcryptSpecification.EMMG_STREAM_CLOSE_REQUEST | 0x0114 / 276 |
| SimulcryptSpecification.EMMG_STREAM_CLOSE_RESPONSE | 0x0115 / 277 |
| SimulcryptSpecification.EMMG_STREAM_ERROR | 0x0116 / 278 |
| SimulcryptSpecification.STREAM_BW_REQUEST | 0x0117 / 279 |
| SimulcryptSpecification.STREAM_BW_ALLOCATION | 0x0118 / 280 |
| SimulcryptSpecification.CW_PROVISION | 0x0201 / 513 |
| SimulcryptSpecification.ECM_RESPONSE | 0x0202 / 514 |
| SimulcryptSpecification.DATA_PROVISION | 0x0211 / 529 |

All parameter names available:

| context | hex/dec. type | length | name |
| :--- | :--- | :--- | :-- |
| EMMG &#8660; MUX | 0x0001 / 1 | 4 | client_id |
| EMMG &#8660; MUX | 0x0002 / 2 | 1 | section_TSpkt_flag |
| EMMG &#8660; MUX | 0x0003 / 3 | 2 | data_channel_id |
| EMMG &#8660; MUX | 0x0004 / 4 | 3 | data_stream_id |
| EMMG &#8660; MUX | 0x0005 / 5 | variable | datagram |
| EMMG &#8660; MUX | 0x0006 / 6 | 2 | bandwidth |
| EMMG &#8660; MUX | 0x0007 / 7 | 1 | data_type |
| EMMG &#8660; MUX | 0x0008 / 8 | 2 | data_id |
| EMMG &#8660; MUX | 0x7000 / 28672 | 2 | error_status |
| EMMG &#8660; MUX | 0x7001 / 28673 | variable | error_information |
| SCS &#8660; ECMG | 0x0001 / 1 | 4 | super_CAS_id |
| SCS &#8660; ECMG | 0x0002 / 2 | 1 | section_TSpkt_flag |
| SCS &#8660; ECMG | 0x0003 / 3 | 2 | delay_start |
| SCS &#8660; ECMG | 0x0004 / 4 | 2 | delay_stop |
| SCS &#8660; ECMG | 0x0005 / 5 | 2 | transition_delay_start |
| SCS &#8660; ECMG | 0x0006 / 6 | 2 | transition_delay_stop |
| SCS &#8660; ECMG | 0x0007 / 7 | 2 | ECM_rep_period |
| SCS &#8660; ECMG | 0x0008 / 8 | 2 | max_streams |
| SCS &#8660; ECMG | 0x0009 / 9 | 2 | min_CP_duration |
| SCS &#8660; ECMG | 0x000A / 10 | 1 | lead_CW |
| SCS &#8660; ECMG | 0x000B / 11 | 1 | CW_per_msg |
| SCS &#8660; ECMG | 0x000C / 12 | 2 | max_comp_time |
| SCS &#8660; ECMG | 0x000D / 13 | variable | access_criteria |
| SCS &#8660; ECMG | 0x000E / 14 | 2 | ECM_channel_id |
| SCS &#8660; ECMG | 0x000F / 15 | 2 | ECM_stream_id |
| SCS &#8660; ECMG | 0x0010 / 16 | 2 | nominal_CP_duration |
| SCS &#8660; ECMG | 0x0011 / 17 | 1 | access_criteria_transfer_mode |
| SCS &#8660; ECMG | 0x0012 / 18 | 2 | CP_number |
| SCS &#8660; ECMG | 0x0013 / 19 | 2 | CP_duration |
| SCS &#8660; ECMG | 0x0014 / 20 | variable | CP_CW_combination |
| SCS &#8660; ECMG | 0x0015 / 21 | variable | ECM_datagram |
| SCS &#8660; ECMG | 0x0016 / 22 | 2 | AC_delay_start |
| SCS &#8660; ECMG | 0x0017 / 23 | 2 | AC_delay_stop |
| SCS &#8660; ECMG | 0x0018 / 24 | variable | CW_encryption |
| SCS &#8660; ECMG | 0x0019 / 25 | 2 | ECM_id |
| SCS &#8660; ECMG | 0x7000 / 28672 | 2 | error_status |
| SCS &#8660; ECMG | 0x7001 / 28673 | variable | error_information |

### smdecode

Command-line tool to output Simulcrypt message content from hex stream:

```
$ smdecode -h
usage: smdecode [-h] [-j] HEXSTREAM

Decode hex stream of DVB Simulcrypt message.

positional arguments:
  HEXSTREAM   raw data hex stream (020201...)

options:
  -h, --help  show this help message and exit
  -j, --json  dump message(s) as JSON object

$ smdecode 030001000e000e00020001000100044ae60000
version: 3
message_type: 1
message_name: CHANNEL_SETUP
message_length: 19
parameter_type: 14
parameter_name: ECM_channel_id
parameter_length: 2
parameter_bytes: 0001
parameter_type: 1
parameter_name: super_CAS_id
parameter_length: 4
parameter_bytes: 4ae60000

$ smdecode -j 030001000e000e00020001000100044ae60000 | jq
{
  "version": 3,
  "message_type": 1,
  "message_name": "CHANNEL_SETUP",
  "message_length": 19,
  "parameter_loop": [
    {
      "type": 14,
      "name": "ECM_channel_id",
      "length": 2,
      "bytes": "0001"
    },
    {
      "type": 1,
      "name": "super_CAS_id",
      "length": 4,
      "bytes": "4ae60000"
    }
  ]
}
```

### SCS/MUX simulators

This library includes sample of [SCS](src/simulcrypt/MUX.py) and
[MUX](src/simulcrypt/SCS.py) component simulators:

```
$ scs -h
usage: scs [-h] [-s HOST] [-p PORT] [-c SEC] [-a AC] [-128] CAS_ID

DVB Simulcrypt V3 SCS component simulator.

positional arguments:
  CAS_ID                super_CAS_id value, 2 or 4 bytes

options:
  -h, --help            show this help message and exit
  -s HOST, --host HOST  ECMG server address or hostname, default is localhost
  -p PORT, --port PORT  TCP port number, default is 2000
  -c SEC, --cp SEC      crypto-period interval, default is min_CP_duration value received from ECMG
  -a AC, --ac AC        Scrambling Group access criteria hex string, default is none
  -128, --csa3          use 128-bit CW (DVB-CSA3/CISSA mode) instead of 64-bit default
```
```
$ mux -h
usage: mux [-h] [-p PORT] [-b BW] [-d] [-v NUM] [--channel_id ID] [--stream_id ID] [--data_id ID] CAS_ID

DVB Simulcrypt MUX component simulator.

positional arguments:
  CAS_ID                super_CAS_id or client_id, 2 or 4 bytes

options:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  TCP port number, default is 2100
  -b BW                 EMM bandwith, default is 100kbps
  -d, --data            output DATA_PROVISION messages, default is not
  -v NUM                protocol version 1-5, default is accept from peer
  --channel_id ID       data_channel_id value, default is 0
  --stream_id ID        data_stream_id value, default is 0
  --data_id ID          data_id value, default is 0
```

## Reference

* [TR 102 035 v1.1.1 Implementation Guidelines of the DVB Simulcrypt Standard](http://www.etsi.org/deliver/etsi_tr/102000_102099/102035/01.01.01_60/tr_102035v010101p.pdf)
* [TS 101 197 v1.2.1 DVB SimulCrypt; Part 1: Head-end architecture and synchronization](http://www.etsi.org/deliver/etsi_ts/101100_101199/101197/01.02.01_60/ts_101197v010201p.pdf)
* [TS 103 197 v1.5.1 Head-end Implementation of SimulCrypt](http://www.etsi.org/deliver/etsi_ts/103100_103199/103197/01.05.01_60/ts_103197v010501p.pdf)

## Author &amp; License

&copy; 2020-2025 Victor Stepanov

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file
except in compliance with the License. You may obtain a copy of the License at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the
License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the License for the specific language governing permissions
and limitations under the License.
