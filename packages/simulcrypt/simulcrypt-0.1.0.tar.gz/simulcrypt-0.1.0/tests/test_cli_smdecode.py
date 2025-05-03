import os


COMMAND = ("python3 -c 'import sys; sys.path.append(\"./src\"); from simulcrypt import smdecode_cli; "
           "sys.exit(smdecode_cli())' ")

def test_cli_smdecode_help(capfd):
    os.system(COMMAND + "--help")
    out, _ = capfd.readouterr()
    assert "Decode hex stream of DVB Simulcrypt message." in out

def test_cli_smdecode_dump(capfd):
    os.system(COMMAND + "020001000e000e00020001000100044ae60000")
    out, _ = capfd.readouterr()
    assert "version: 2" in out
    assert "message_type: 1" in out
    assert "message_name: CHANNEL_SETUP" in out
    assert "message_length: 19" in out
    assert "parameter_type: 14" in out
    assert "parameter_name: ECM_channel_id" in out
    assert "parameter_length: 2" in out
    assert "parameter_bytes: 0001" in out
    assert "parameter_type: 1" in out
    assert "parameter_name: super_CAS_id" in out
    assert "parameter_length: 4" in out
    assert "parameter_bytes: 4ae60000" in out

def test_cli_smdecode_dump_json(capfd):
    os.system(COMMAND + "-j 020001000e000e00020001000100044ae60000")
    out, _ = capfd.readouterr()
    assert ('{"version":2,"message_type":1,"message_name":"CHANNEL_SETUP","message_length":19,"parameter_loop":['
            '{"type":14,"name":"ECM_channel_id","length":2,"bytes":"0001"},{"type":1,"name":"super_CAS_id","length":4,'
            '"bytes":"4ae60000"}]}') in out
