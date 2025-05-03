import sys
import os
import random

import pytest

try:
    from simulcrypt import SimulcryptParameter, SimulcryptMessage
    from simulcrypt.specification import SimulcryptSpecification as spec
except ImportError:
    sys.path.append(os.path.join(os.path.join(os.path.dirname(__file__), ".."), "src"))
    from simulcrypt import SimulcryptParameter, SimulcryptMessage
    from simulcrypt.specification import SimulcryptSpecification as spec


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


def test_create_message_with_bytes():
    data = b'\x01\x02\x01\x00\x01\x00'
    scm = SimulcryptMessage(data)
    assert data == scm.data, "should be b'\x01\x02\x01\x00\x01\x00'"
    with pytest.raises(ValueError):
        scm = SimulcryptMessage()

def test_create_1k_random_bytes_messages():
    for _ in range(1000):
        data = random.randbytes(random.randint(1,50))
        scm = SimulcryptMessage(data)
        assert not scm.is_simulcrypt

def test_create_message_with_parameters():
    scm = SimulcryptMessage(version=2, type=0x0002, ECM_channel_id=1)
    assert scm.version == 2
    assert scm.is_simulcrypt
    assert scm.is_valid
    scm = SimulcryptMessage(type=0x0002, ECM_channel_id=1)
    assert scm.version == 3
    assert scm.is_simulcrypt
    assert scm.is_valid

def test_create_message_type_parameter():
    with pytest.raises(TypeError):
        _ = SimulcryptMessage(version=2)
    with pytest.raises(TypeError):
        _ = SimulcryptMessage(version=2, type='0x0300')
    with pytest.raises(ValueError):
        _ = SimulcryptMessage(version=2, type=0x0300)

def test_create_message_version_parameter():
    with pytest.raises(TypeError):
        _ = SimulcryptMessage(version='2', type=0x0002)
    with pytest.raises(ValueError):
        _ = SimulcryptMessage(version=7, type=0x0002)

def test_create_message_parameters():
    scm = SimulcryptMessage(version=3, type=0x00002, ECM_channel_id=1)
    assert scm.version == 3
    with pytest.raises(TypeError):
        scm = SimulcryptMessage(version=3, type=0x0002, E_channel_id=1)
    scm = SimulcryptMessage(version=3, type=0x0111, data_id=1)
    assert scm.version == 3
    with pytest.raises(TypeError):
        scm = SimulcryptMessage(version=3, type=0x0111, ECM_id=1)

def test_message_parameter_length_by_name():
    for type_, value in spec.ECMG_PARAMETER.items():
        assert SimulcryptParameter.length(0x0001, value) == spec.ECMG_PARAMETER_LEN[type_]
    for type_, value in spec.EMMG_PARAMETER.items():
        assert SimulcryptParameter.length(0x0111, value) == spec.EMMG_PARAMETER_LEN[type_]

def test_message_parameter_length_by_type():
    for type_ in spec.ECMG_PARAMETER:
        assert SimulcryptParameter.length(0x0001, type_) == spec.ECMG_PARAMETER_LEN[type_]
    for type_ in spec.EMMG_PARAMETER:
        assert SimulcryptParameter.length(0x0111, type_) == spec.EMMG_PARAMETER_LEN[type_]

def test_message_parameter_type_by_name():
    assert SimulcryptParameter.type_(0x201, 'ECM_channel_id') != 0
    assert SimulcryptParameter.type_(0x201, 'ECM_channel') == 0

def test_cannot_handle_data_and_parameters():
    data = b'\x01\x02\x01\x00\x01\x00'
    with pytest.raises(RuntimeError):
        _ = SimulcryptMessage(data, version=3, type=0x0201)

def test_message_version():
    data = b'\x06\x02\x01\x00\x01\x00'
    scm = SimulcryptMessage(data)
    assert not scm.is_simulcrypt, "should be invalid since version isn't correct"

def test_message_consistency():
    test_data = [
        '03021100da0001000406aa0000000300020000000400020000000800020000000500'
        'bc47400000082407c420558000004007486003318194da29eb5de60b8096b16395a1'
        'b3b63a9084da29eb5de60b8096b16395a1b3b63a9be02b098f3b25c8d9bf69f98261'
        '6804f86003320194b0f6f2636e27bfd48481acfe6dce140084b0f6f2636e27bfd484'
        '81acfe6dce140be02b098f3b25c8d9bf69f982616804f5e994b67fe419497fffffff'
        'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
        'ffffffffffffffffffffffffffffffffffffff',

        '020001000e000e00020001000100044ae60000',     # EMR4.0

        '030014000e0001000406aa0000000300020000'
        '030014000e0001000406aa0000000300020000',
        '03001100130001000406aa00000003000200000002000101',
        '03001300130001000406aa00000003000200000002000101',
        '030111001f0001000406aa0000000300020000000400020000000700010000080002'
        '0000',
        '030113001f0001000406aa0000000300020000000400020000000700010000080002'
        '0001',
        '030117001a0001000406aa0000000300020000000400020000000600020064',
        '030118001a0001000406aa0000000300020000000400020000000600020064',

        '03021100da0001000406aa0000000300020000000400020000000800020000000500'
        'bc474000100082423a420448000004023288022714000b948469d5d603b7568b01f5'
        '56bd9840ace5e4ffffffffffffff8000000000000000000000000000000000000000'
        '00000000000000000000000000000000000000000000000000000000000000000000'
        '00000000000000000000000000000000000000000000000000000000000000000000'
        '00000000000000000000000000000000000000000000000000000000000000000000'
        '00000000000000000000000000000000000000020001000e000e0002000000010004'
        '06aa0000',

        '030012000e0001000406aa0000000300020000',
        '03001300130001000406aa00000003000200000002000101',
        '020001000e000e000200000001000406aa0000',

        '0200030039000e00020000000200010100030002000000040002000000070002012c'
        '000800'
        '0200000009000200d2000a000101000b000102000c00024e20',

        '0201010018000e00020000000f0002000000100002012c001900020000',
        '0201030017000e00020000000f000200000011000101001900020000',

        '020201003c000e00020000000f000200000012000274880014000a748845cbbe0000'
        '0000be'
        '0014000a748945cbc000000000c0000d000a900100060001006a0001',

        '030005000c000e00020001700000020004',
        '0300050012000e00020001700000027001700100021234',
        '030005001c000e000200017000000270017001000c58206973206d697373696e67',

        '02020200d2000e00020000000f00020000001200027488001500bc47400010008070'
        '6641000004250008805da3030000888a43107f1345cbbece00000000000000000000'
        '000045cbc0d000000000000000000000000059cb91488205f0f9970d5f22d10924f3'
        'a7ad91b3cc6d5c4091fbdae8916faa5c8d09000300000000000000b5ae87a7eca7ad'
        'baffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
        'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
        'ffffffffffffffffffffff',

        '0200020006000e00020001',
        '0200030039000e0002000100020001000003000201f40004000200000007000200fa'
        '0008000201f4000900020032000a000101000b000102000c000207d0',
        '020201004c000e00020001000f00020001001200020db1001400120db16875e451c5'
        '92b327357088d8444874a5001400120db246b5c044d45f95d5d7017f92efde9560001'
        '3000201c2000d0004000000d0',
        '0202020053000e00020001000f00020001001200020db10015003d81703a0001fffff'
        'fff000000005556845e7b55b25817e9eec530aff3361dcf8fe08617e93d411100dce5'
        '72f0d58e5d58f18fff44ca8b064dc4ef984e23'
        ]
    for data in test_data:
        scm = SimulcryptMessage(bytes.fromhex(data))
        assert scm.is_simulcrypt
        assert scm.is_valid
        assert len(bytes.fromhex(data)) == len(scm.data) + len(scm.leftover)

def test_malformed_messages():
    test_data = [
        '020001000e000e0002000000010004060000',     # wrong length
        '0300010000',                               # wrong length
        '0300070000',                               # wrong length
        '030700',                                   # invalid Simulcrypt
        '0300070006000e00020001',                   # wrong type
        '000001000e000e000200000001000406aa0000',   # wrong version
        '060001000e000e000200000001000406aa0000']   # wrong version
    for data in test_data:
        scm = SimulcryptMessage(bytes.fromhex(data))
        assert scm.error_message
        assert not scm.is_simulcrypt

def test_message_parameters():
    data = ('020201003c'
            '000e00020000'
            '000f00020000'
            '001200027488'
            '0014000a748845cbbe00000000be'
            '0014000a748945cbc000000000c0'
            '000d000a900100060001006a0001')
    scm = SimulcryptMessage(bytes.fromhex(data))
    assert scm.version == 2
    assert scm.type == 0x0201  # CW_provision
    assert len(scm.parameters) == 6

# pylint: disable=W0104
def test_create_message_with_parameters_more():
    scm = SimulcryptMessage(version=3,
                            type=EMMG_CHANNEL_SETUP,
                            client_id=0x06aa0000,
                            data_channel_id=0,
                            section_TSpkt_flag=1)
    assert scm.data.hex() == '03001100130001000406aa00000003000200000002000101'
    assert scm.version == 3
    assert scm.type == EMMG_CHANNEL_SETUP
    assert scm.client_id == 0x06aa0000
    assert scm.data_channel_id == 0
    assert scm.section_TSpkt_flag == 1
    with pytest.raises(AttributeError):
        scm.bandwidth is None
    with pytest.raises(AttributeError):  # different context
        scm.super_CAS_id == 1                                       # pylint: disable=W0104

    parameters = {'version': 2, 'type': CW_PROVISION,
                  'ECM_channel_id': 0,'ECM_stream_id': 0, 'CP_number': 29832,
                  'CP_CW_combination': [
                        bytes.fromhex('748845cbbe00000000be'),
                        bytes.fromhex('748945cbc000000000c0')],
                  'access_criteria': bytes.fromhex('900100060001006a0001')}
    scm = SimulcryptMessage(**parameters)
    assert scm.version == 2
    assert scm.type == CW_PROVISION
    assert scm.data.hex() == ('020201003c'
                              '000e00020000'
                              '000f00020000'
                              '001200027488'
                              '0014000a748845cbbe00000000be'
                              '0014000a748945cbc000000000c0'
                              '000d000a900100060001006a0001')
    assert scm.ECM_channel_id == 0
    assert scm.ECM_stream_id == 0
    assert scm.CP_number == 29832
    assert scm.CP_CW_combination == [bytes.fromhex('748845cbbe00000000be'),
                                     bytes.fromhex('748945cbc000000000c0')]
    assert scm.access_criteria == bytes.fromhex('900100060001006a0001')
    with pytest.raises(AttributeError):
        scm.error_status is None
    with pytest.raises(AttributeError):
        scm.super_CAS_id is None
    with pytest.raises(AttributeError):  # wrong name
        scm.Super_CAS_id == 1                                       # pylint: disable=W0104

def test_access_message_parameters():
    m1 = SimulcryptMessage(bytes.fromhex('020201003c000e00020000000f000200000012000274880014000a748845cbbe00000000be'
                                         '0014000a748945cbc000000000c0000d000a900100060001006a0001'))
    assert [param.name for param in m1.parameters] == ['ECM_channel_id', 'ECM_stream_id', 'CP_number',
                                                       'CP_CW_combination', 'CP_CW_combination', 'access_criteria']
    m2 = SimulcryptMessage(version=2, type=spec.CW_PROVISION, ECM_channel_id=0, ECM_stream_id=0, CP_number=0x7488,
                           CP_CW_combination=[bytes.fromhex('748845cbbe00000000be'),
                                              bytes.fromhex('748945cbc000000000c0')],
                           access_criteria=bytes.fromhex('900100060001006a0001'))
    assert m2.data == m1.data
    with pytest.raises(AttributeError):
        m1.client_id == 1
    with pytest.raises(AttributeError):
        m1.section_TSpkt_flag == 1
    with pytest.raises(AttributeError):
        m1.lead_CW == 1

def test_create_message_parameter_length():
    with pytest.raises(ValueError):
        _ = SimulcryptMessage(version=3,
                                type=EMMG_CHANNEL_SETUP,
                                client_id=0x06aa0000,
                                data_channel_id=0,
                                section_TSpkt_flag=256)   # out of range
    with pytest.raises(ValueError):
        _ = SimulcryptMessage(version=3,
                                type=EMMG_CHANNEL_SETUP,
                                client_id=0x06aa0000,
                                data_channel_id=70000,    # out of range
                                section_TSpkt_flag=1)
    with pytest.raises(ValueError):
        _ = SimulcryptMessage(version=3,
                                type=EMMG_CHANNEL_SETUP,
                                client_id=-1,             # signed
                                data_channel_id=0,
                                section_TSpkt_flag=1)

def test_message_optional_parameters():
    data = ('0300030039'
            '000e00020000'
            '0002000101'
            '000300020000'
            '000400020000'
            '00070002012c'
            '000800020000'
            '0009000200d2'
            '000a000101'
            '000b000102'
            '000c00024e20')
    scm = SimulcryptMessage(bytes.fromhex(data))
    assert scm.is_valid
    with pytest.raises(AttributeError):
        scm.AC_delay_start is None
    with pytest.raises(AttributeError):
        scm.AC_delay_stop is None
    with pytest.raises(AttributeError):
        scm.transition_delay_start is None
    with pytest.raises(AttributeError):
        scm.transition_delay_stop is None
    with pytest.raises(AttributeError):
        scm.data_id is None                                         # pylint: disable=W0104
    parameters = {'version': 3,
                  'type': ECMG_CHANNEL_STATUS,
                  'ECM_channel_id': 0,
                  'section_TSpkt_flag': 1,
                  'AC_delay_start': None,
                  'AC_delay_stop': None,
                  'delay_start': 0,
                  'delay_stop': 0,
                  'transition_delay_start': None,
                  'transition_delay_stop': None,
                  'ECM_rep_period': 300,
                  'max_streams': 0,
                  'min_CP_duration': 210,
                  'lead_CW': 1,
                  'CW_per_msg': 2,
                  'max_comp_time': 20000}
    assert SimulcryptMessage(**parameters).data == bytes.fromhex(data)

def test_message_compliance():
    test_data = ['020001'              # two instances of super_CAS_id
                 '0016'
                 '000e00020000'
                 '0001000406000000'
                 '0001000406000000',
                 '020001'              # wrong length of super_CAS_id
                 '000c'
                 '000e00020000'
                 '000100020600',
                 '020001'              # ECM_rep_period not allowed
                 '0014'
                 '000e00020000'
                 '0001000406000000'
                 '000700020001',
                 '020001'              # super_CAS_id missing
                 '0006'
                 '000e00020000',
                 '010101'              # ECM_id not allowed in V1
                 '0018'
                 '000e00020000'
                 '000f00020000'
                 '00100002012c'
                 '001900020000',
                 '010201'              # wrong CP_CW_combination length
                 '003e'
                 '000e00020000'
                 '000f00020000'
                 '001200027488'
                 '0014000b748845cbbe00000000be00'
                 '0014000b748945cbc000000000c000'
                 '000d000a900100060001006a0001']
    test_data.append(
        SimulcryptMessage(
            version=2,
            type=CW_PROVISION,
            ECM_channel_id=1,
            ECM_stream_id=2).data.hex())
    for data in test_data:
        scm = SimulcryptMessage(bytes.fromhex(data))
        assert scm.error_message
        assert not scm.is_valid


if __name__ == "__main__":
    pytest.main()
