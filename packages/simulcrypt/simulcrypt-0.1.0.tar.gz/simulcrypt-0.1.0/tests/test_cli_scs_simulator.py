import os


COMMAND = ("python3 -c 'import sys; sys.path.append(\"./src\"); from simulcrypt import scs_simulator_cli; "
           "sys.exit(scs_simulator_cli())' ")

def test_cli_scs_simulator_help(capfd):
    os.system(COMMAND + "--help")
    out, _ = capfd.readouterr()
    assert "DVB Simulcrypt V3 SCS component simulator." in out
