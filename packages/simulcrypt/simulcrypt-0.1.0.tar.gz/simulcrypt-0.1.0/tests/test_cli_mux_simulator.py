import os


COMMAND = ("python3 -c 'import sys; sys.path.append(\"./src\"); from simulcrypt import mux_simulator_cli; "
           "sys.exit(mux_simulator_cli())' ")

def test_cli_mux_simulator_help(capfd):
    os.system(COMMAND + "--help")
    out, _ = capfd.readouterr()
    assert "DVB Simulcrypt MUX component simulator." in out
